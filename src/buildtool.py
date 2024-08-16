from src.kubeutil import KubeUtil
from os.path import relpath
from os import _exit
import click
import time
from subprocess import Popen, PIPE
import time
from threading  import Thread
from queue import Queue, Empty

class BuildTool:
    project_path: str
    # mount_proces

    # REF: https://stackoverflow.com/questions/375427/a-non-blocking-read-on-a-subprocess-pipe-in-python
    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def __init__(self, project_path:str):
        self.project_path = project_path

        #TO DO: find dockerfile
        
        mounted = self.mount_directory()
        if(not mounted):
            click.echo("Could not mount directory in first try, trying again.")
            mounted = self.mount_directory()
        if(not mounted):
            print("Error in mounting project directory, please try again.")
            _exit(status=1)

    # I know this is bad, didn't find an alternative though. Minikube doesn't have an SDK and I had a lot of adventures with mounting volumes :/        
    def mount_directory(self) -> bool:
        self.mount_process = Popen(['minikube', 'mount', self.project_path + ":/kanikotool"], stdout=PIPE, bufsize=1,universal_newlines=True, encoding="utf-8")
        q = Queue()
        
        t = Thread(target=self.enqueue_output, args=(self.mount_process.stdout, q))
        t.daemon = True
        t.start()

        TIME_OUT = 15
        start = time.time()

        while(True):
            # print(time.time()-start)
            if(time.time()-start > TIME_OUT):
                self.mount_process.terminate()
                return False
            poll = self.mount_process.poll()
            if(poll is not None):
                print("Error in mounting project directory, please try again.")
                return False
            
            try:  line = q.get_nowait() # or q.get(timeout=.1)
            except Empty:
                pass
            else:
                print(line)
                if("Successfully mounted" in line):
                    print("Mounted project directory onto cluster.")
                    return True

    def submit_job(self, username_plain, auth_string, image_name):
        kube_util = KubeUtil()
        try:
            kube_util.create_secret(auth_string = auth_string)
            kube_util.create_volume(path="/kanikotool")
            kube_util.create_volume_claim()
            kube_util.create_pod(username_plain=username_plain, image_name=image_name)
            status = "Pending"
            while(status == "Pending" or status == "Running"):
                status = kube_util.get_pod_status()
                click.echo(f"Pod status: {status}")
                time.sleep(1)
            click.echo(f"Pod status: {status}")
            kube_util.get_logs()
        except Exception as e:
            click.echo("Build failed, tool will cleanup - please try again.", err=True)
            print(e)
        finally:
            kube_util.cleanup()
            self.mount_process.terminate()