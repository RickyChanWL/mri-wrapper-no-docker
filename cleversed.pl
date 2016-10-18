#!/usr/bin/perl
use v5.14;
binmode STDOUT, ":utf8";

my $pattern= $ARGV[0];
my $tostring= $ARGV[1];
if($#ARGV!=1){
  say "fucked";
  exit();
}
while(<STDIN>){

  $_=~s/$pattern/$tostring/g;
  print $_;

}
