import sys
import argparse


singularity_base = """
Bootstrap: docker
From: {base_img}

%post
    apt-get -y update
    apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    git \
    python \
    python-pip \
    python-setuptools
    
    apt-get -y install {apt_packages}

{pip_packages}




    {more}
"""

docker_base = """
FROM {base_img}

RUN apt-get -y update
RUN apt-get -y install {apt_packages}

RUN pip install --upgrade setuptools

{pip_packages}


{more}
"""

# -----------------------------

# we want to know exactly which packaged failed to install
def make_pip_install(name, docker=False):
    pip_packages = open(name, 'r').read().split('\n')
    prefix = '   '
    if docker:
        prefix = 'RUN '

    pip_packages = map(lambda p: p.strip(), pip_packages)
    pip_packages = filter(lambda p: len(p) > 0, pip_packages)
    return '\n'.join([f'{prefix} pip install --no-deps {p}' for p in pip_packages])


def make_file(name, script, base_img, apt_packages, pip_packages, more=''):
    script = (script
        .replace('{base_img}', base_img)
        .replace('{apt_packages}', apt_packages)
        .replace('{pip_packages}', pip_packages)
        .replace('{more}', more))

    with open(name, 'w') as f:
        f.write(script)

    return script


def generate_conf(generate_singularity=True, generate_docker=False, framework="tensorflow", tasks="base"):

    apt_packages = (open('../configurations/singularity_dependencies/apt_packages.txt', 'r')
        .read()
        .replace('\n', ' '))
    
    # ROCm Image
    # ---------------------------------------------------
    # Remove all the reference to useless python versions
    # and make python3.6 the default
    more_rocm = ' && '.join([
        'rm /usr/bin/python3',
        'rm /usr/bin/python',
        'ln -s /usr/bin/python3.6 /usr/bin/python',
        'ln -s /usr/bin/python3.6 /usr/bin/python3'
    ])
    
    if generate_singularity:
        if framework == "tensorflow":
            if tasks == "base":
                make_file(
                    'Singularity_{}_{}.def'.format(framework, tasks),
                    singularity_base,
                    'nvcr.io/nvidia/cuda:9.0-cudnn7-runtime-ubuntu16.04',
                    apt_packages,
                    make_pip_install('../configurations/singularity_dependencies/tensorflow/requirements.txt')
                )
            else:
                print("select tasks : default = base")
                sys.exit(0)
        else:
            print("choose a frameworks [tensorflow , pytorch]")
            sys.exit(0)
    
    elif generate_docker:
        if framework == "tensorflow":
            if tasks == "base":
                make_file(
                    'Dockerfile_{}_{}.def'.format(framework, tasks),
                    docker_base,
                    'nvcr.io/nvidia/cuda:9.0-cudnn7-runtime-ubuntu16.04',
                    apt_packages,
                    make_pip_install('../requirements.txt'),
                    more=f'RUN {more_rocm}'
                )
            else:
                print("select tasks : default = base")
                sys.exit(0)
        else:
            print("choose a frameworks [tensorflow , pytorch]")
            sys.exit(0)
    
    else:
        print("select if you want docker or singularity")
        sys.exit(0)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Containers Singularity / Dockers')
    parser.add_argument('--generate_singularity', type=bool, default=True)
    parser.add_argument('--generate_docker', type=bool, default=False)
    parser.add_argument('--framework', type=str, default="tensorflow")
    parser.add_argument('--tasks', type=str, default="base")    
    args = parser.parse_args()
    print(args)
    
    generate_conf(generate_singularity = args.generate_singularity, 
                  generate_docker = args.generate_docker, 
                  framework=args.framework, tasks=args.tasks)   

            
