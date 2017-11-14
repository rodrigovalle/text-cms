import inotify.adapters
import threading # time to put on the big boi pants
import os

def _main():
    i = inotify.adapters.Inotify()
    i.add_watch(b'content/articles')

    last_modified_map = {}
    try:
        for event in i.event_gen():
            if event is not None:
                (header, type_names, watch_path, filename) = event

                if 'IN_DELETE' in type_names or 'IN_MOVED_FROM' in type_names:
                    # TODO: Remove the file from redis.
                    print(filename + " deleted.")
                elif 'IN_MOVED_TO' in type_names or 'IN_MODIFY' in type_names or 'IN_CREATE' in type_names:
                    last_modified = int(round(os.path.getmtime('content/articles/' + filename)))
                    if filename not in last_modified_map or last_modified_map[filename] != last_modified:
                        last_modified_map[filename] = last_modified
                        print(filename + " modified.")
                        # TODO: Parse the new file.

    finally:
        i.remove_watch(b'content/articles')

if __name__ == '__main__':
   _main()