Use mri-wrapper without docker in [mri-wrapper](https://github.com/gifford-lab/mri-wrapper)

## Dependencies
* [Caffe and pycaffe](http://caffe.berkeleyvision.org/installation.html)
* [caffe-cnn](https://github.com/gifford-lab/caffe-cnn)
* [Mri-app](http://mri.readthedocs.org/en/latest/index.html)

## Setting up
change the root directory variables as your actual root directories for Caffe, caffe-cnn and Mri-app in [mriwrapperlib.py](https://github.com/RickyChanWL/mri-wrapper-no-docker/blob/master/mriwrapperlib.py)

## How
1. Create a working directory(for example, example)
2. Prepare the same data files and model files as same as [mri-wrapper](https://github.com/gifford-lab/mri-wrapper)
3. Put data files in wd/data and model files in wd/model
4. In train.txt, test.txt, valid.txt, the path should be absolute path of the data files
5. Run the mriwrapper, you should keep the invisible window opened, otherwise, the process will be terminated
```
mriwrapper example 0 #mriwrapper $wd $GPUNUM
```
