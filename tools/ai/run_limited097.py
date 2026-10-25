"""Run a test controller and its workers on one shared small CPU set."""
import argparse, subprocess
import psutil

def main():
    p=argparse.ArgumentParser();p.add_argument('--cpus',default='0,2,4,6');p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();command=a.command
    if command and command[0]=='--':command=command[1:]
    if not command:p.error('command required after --')
    psutil.Process().cpu_affinity([int(x) for x in a.cpus.split(',')])
    raise SystemExit(subprocess.call(command))

if __name__=='__main__':main()
