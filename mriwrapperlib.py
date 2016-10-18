#setting up ROOT for dependency
#cleversed.pl
import os,sys
from parseMRI import parseMRI
from os.path import dirname,exists,join,realpath
from os import system,makedirs,chdir,getcwd,makedirs

def mriwrapper(folder,gpunum):
    mri_ROOT = '/uac/gds/wlchan/mydrive/Mri-app' #set the path for Mri-app !!!!!!!!!!!
    CAFFECNN_ROOT = '/uac/gds/wlchan/mydrive/caffe-cnn' #set the path for caffe-cnn !!!!!!!!!!
    CAFFE_ROOT = '/uac/gds/wlchan/mydrive/caffecudnn' #set the path for caffe !!!!!!!!!!!!
    library_dir = dirname(realpath(__file__))
    folder_dir = realpath(folder)

    chdir(folder_dir)
    runparam_file = join(folder_dir,'model','runparam_docker.list')
    with open(runparam_file,'r') as f:
        runparamdata = f.readlines()
    runparams = {}
    #read the file into runparams hash
    for i in range(len(runparamdata)):
        line = runparamdata[i].strip().split()
        runparams.update({line[0]:line[1]})
        print line[0] +' : '+str(line[1])
    order = runparams['ORDER']

    mri_maxiter = int(runparams['MRI_MAXITER'])

    runparams['TRAINVAL'] = folder_dir+'/model/trainval.prototxt' #set path for trainval !!!!!!!!!!!!
    runparams['SOLVER'] = folder_dir+'/model/solver.prototxt' #set path for solver !!!!!!!!!!!!!
    runparams['DEPLOY'] = folder_dir+'/model/deploy.prototxt' #set path for deploy !!!!!!!!!!!
    runparams['HYPER'] = folder_dir+'/model/hyperparams.txt' #set path for hyperparams.txt !!!!!!!!!!!!!!
    runparams['model_topdir'] = folder_dir #set path for data !!!!!!!!!!!!!!!!
    with open(folder_dir+'/model/modelname','r') as f: # set path for modelname !!!!!!!!!!!!!!
        modelname = [x.strip() for x in f][0]

    mrifolder = join(runparams['model_topdir'],modelname,'mri') #check runparam file !!!!
    mri_bestfolder = join(runparams['model_topdir'],modelname,'mri','best') #check runparam file !!!!
    deploy_tempalte = os.path.join(folder_dir,'deploy.prototxt') #naming
    trainval_file = join(folder_dir,'trainval.prototxt') #naming
    solver_file = join(folder_dir,'solver.prototxt') #naming
    param_file = join(folder_dir,'param.list') #naming
    train_params = join(folder_dir,'train.params') #naming
    hyperparam = join(folder_dir,'hyperparams.txt') #naming
    mrilogfile = join(mrifolder,'mri.log') #naming

    transfer_params = {'max_iter','snapshot','test_interval','display'}

    with open(param_file,'w') as f:
        f.write('output_topdir %s\n' % runparams['model_topdir'])
        f.write('caffemodel_topdir %s\n' % mri_bestfolder)
        f.write('batch2predict mri-best\n')
        f.write('gpunum %s\n' % gpunum)
        f.write('model_name %s\n' % modelname)
        f.write('batch_name %s\n' % 'mri-best')
        f.write('trial_num %s\n' % runparams['train_trial'])
        f.write('optimwrt %s\n' % runparams['optimwrt'])
        f.write('outputlayer %s\n' % runparams['outputlayer'])
        if 'predict_on' in runparams:
            f.write('predict_filelist %s\n' % runparams['predict_on'])
        for code in ['deploy2predictW','caffemodel2predictW','data2predict','predict_outdir']:
            if code in runparams:
                f.write(code+' %s\n' % runparams[code])

    if 'trainMRI' in order:
        #system(' '.join(['cp ',runparams['TRAINVAL'],trainval_file]))
        goodcall(' '.join(['cp ',runparams['DEPLOY'],deploy_tempalte]))
        goodcall(' '.join(['cp ',runparams['HYPER'],hyperparam]))
        goodcall(' '.join(['cat', runparams['TRAINVAL'],'|',library_dir+'/cleversed.pl','/data/data',folder_dir+'/data','>',trainval_file]))
        with open(solver_file,'w') as outs,open(runparams['SOLVER'],'r') as ins:
            for x in ins:
                key = x.strip().split(':')[0].split(' ')[0]
                # transfer_params search_...
                if key in transfer_params:
                    newkey = 'search_'+key
                    outs.write('%s\n' % ':'.join([key,runparams[newkey]]))
                else:
                    outs.write(x)

        goodcall(' '.join(['echo','\'device_id: '+gpunum+'\'','>>',solver_file]))
        #delete existing /cl109_/128_G/mri
        if exists(mrifolder):
            print 'output folder ' + mrifolder + ' exists! Will be removed'
            goodcall('rm -r ' + mrifolder)

        print 'Trainning MRI'
        key = '\'MRIDIR\''
        value = '\'' + mrifolder +'\''
        #Rscript subPlaceholder.R ./config.txt.template 'MRIDIR' '/cl109_/128_G/mri' ./config.txt
        goodcall(' '.join(['Rscript', join(library_dir,'subPlaceholder.R'),join(library_dir,'config.txt.template'),key,value,join(folder_dir,'gen_config')]))

        key = '\'' + ';'.join(['MRIDIR','CAFFEROOT','INFO']) + '\''
        value = '\'' + ';'.join([mrifolder,CAFFE_ROOT,runparams['debugmode']]) + '\''
        #Rscript subPlaceholder.R ./config.template 'MRIDIR;CAFFEROOT;INFO' '/cl109_/128_G/mri;$CAFFE_ROOT;INFO' $mri_ROOT/mriapp/config
        goodcall(' '.join(['Rscript', join(library_dir,'subPlaceholder.R'),join(library_dir,'config.template'),key,value,join(folder_dir,'mri_config')]))
        #python generate_tasks.py random -n $mri_maxiter
        #generate tasks in mrifolder/task/... used ./config.txt and configuration file in current folder
        goodcall('python '+library_dir+'/generate_tasks.py random -n '+str(mri_maxiter)+' --config gen_config')
        #python MriApp.py using config file in here
        goodcall('python '+mri_ROOT+'/mriapp/MriApp.py --config mri_config')

    if 'update' in order:
        #system(' '.join(['cp ',runparams['TRAINVAL'],trainval_file]))
        goodcall(' '.join(['cat', runparams['TRAINVAL'],'|',library_dir+'/cleversed.pl','/data/data',folder_dir+'/data','>',trainval_file]))
        goodcall(' '.join(['cp ',runparams['SOLVER'],solver_file]))
        goodcall(' '.join(['cp ',runparams['DEPLOY'],deploy_tempalte]))
        goodcall(' '.join(['cp ',runparams['HYPER'],hyperparam]))
        goodcall(' '.join(['echo','\'device_id: '+gpunum+'\'','>>',solver_file]))

        print 'Retrieving best param from Mri'
        refile = folder_dir+'/mri_summary'
        goodcall(' '.join(['grep \'Final Extreme\'', mrilogfile, '>',refile]))
        #call parseMRI returned a dict
        re= parseMRI(refile,runparams['optimwrt'])
        print 'best params:'
        print re

        trainsolver = join(mri_bestfolder,'solver.prototxt')
        trainproto = join(mri_bestfolder,'trainval.prototxt')
        testdeploy = join(mri_bestfolder,'deploy.prototxt')
        if not exists(mri_bestfolder):
            makedirs(mri_bestfolder)

        key = '\'' + ';'.join([x for x in re.keys()]) + '\''
        value = '\'' + ';'.join([re[x] for x in re.keys()]) + '\''

        goodcall(' '.join(['Rscript', os.path.join(library_dir,'subPlaceholder.R'),solver_file,key,value,trainsolver]))
        goodcall(' '.join(['Rscript', os.path.join(library_dir,'subPlaceholder.R'),trainval_file,key,value,trainproto]))
        goodcall(' '.join(['Rscript', os.path.join(library_dir,'subPlaceholder.R'),deploy_tempalte,key,value,testdeploy]))
    #test.txt location == folder_dir/data/test.txt
    #train.txt location valid.txt location specified in trainval
    if 'trainCaffe' in order:
        print 'Training caffe on best mri-params'
        goodcall(' '.join(['python',CAFFECNN_ROOT+'/run.py','train',param_file]))

    if 'testCaffe' in order:
        print 'Testing caffe on best mri-params'
        goodcall(' '.join(['python',CAFFECNN_ROOT+'/run.py','test',param_file]))

    if 'testEvalCaffe' in order:
        print 'Evaluating caffe on best mri-params'
        goodcall(' '.join(['python',CAFFECNN_ROOT+'/run.py','test_eval',param_file]))

    if 'predictCaffe' in order:
        print 'Predict with a trained Caffe model'
        goodcall(' '.join(['python',CAFFECNN_ROOT+'/run.py','pred',param_file]))
def goodcall(command):
    print command
    if not system(command) ==0:
        raise RuntimeError('call error: '+command)
