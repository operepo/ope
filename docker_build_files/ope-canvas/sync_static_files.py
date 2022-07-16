import os
import logging

from watchfiles import run_process

# Quiet logging from watchfiles
wf_logger = logging.getLogger('watchfiles.main')
wf_logger.setLevel(logging.ERROR)


def on_changes_detected(changes):
    print(f"Public files changed, rsync started.")

def main():
    public_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/public')
    sendfile_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/sendfile')
    rsync_cmd = f"""rsync -av --delete "{public_folder}" "{sendfile_folder}"  """

    print(f"Watching for file changes in {public_folder}.")
    runs = run_process(
	public_folder,
        target=rsync_cmd,
        target_type='command',
        debounce=1000,  # don't re-run for every file,
        callback=on_changes_detected,
    )

    printf(f"Stopping file watcher, {runs} change events processed.")



if __name__ == "__main__":
    main()

