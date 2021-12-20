import pkg_resources
import platform

COURSE_PYTHON_VERSION = '3.9'
COURSE_MIN_RECOMMENDED_PYTHON_VERSION = '3.6'

def verify_python_installation():
    python_version = platform.python_version()
    print(f'Your python version: {python_version}')
    if python_version[:3] != COURSE_PYTHON_VERSION:
        warning_msg = f'~ Your python version is not the same as the version used by the autograder ({COURSE_PYTHON_VERSION}).\n'\
                      f'~ The minimum recommended version is {COURSE_MIN_RECOMMENDED_PYTHON_VERSION}.'
        print(warning_msg)

def verify_libraries_installation():
    with open('rait_env.yml', 'r') as f:
        yaml_contents = f.readlines()
    dependencies = [line.strip('- \n') for line in yaml_contents[yaml_contents.index('dependencies:\n')+2:] if ':' not in line]
    try:
        pkgs = set([str(pkg) for pkg in pkg_resources.require(dependencies)])
        print('✅  All libraries installed!')
        for pkg in pkgs:
            pkg_name = pkg.split()[0]
            if pkg_name in dependencies:
                print(f'\t{pkg}')
    except pkg_resources.DistributionNotFound as e:
        print('⚠️ Missing library')
        print(e)
    except Exception as e:
        print('❌️ Error')
        print(e)

if __name__ == '__main__':
    verify_python_installation()
    verify_libraries_installation()
