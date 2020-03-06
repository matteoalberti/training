#! bin/bash/

cd /home/albertilabs/MHPC_Thesis_NextCloud/benchmarks/Mlperf_training/Singularity

dir=sif


python3 generate_container.py $@

if [[ ! -e $dir ]]; then
    mkdir $dir
fi

sudo singularity build $dir/STF.sif Singularity_tensorflow_base.def