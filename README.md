# Distributed FileSystem

## Working
- The file system is a multi-threaded distributed file system. It utilizes underlying operating system's filesystem for basic operations such as creating file or directories, reading, writing, deleting and renaming files and directories. It provides enhanced features such as fault tolerance and distributed storage. 
- The architecture is based on Google File System (GFS) comprising master and slave servers. In this system, there is a central server which manages storing the data into storage servers. For each user, the data is written into two storage servers to allow for fault tolerance. 
- In order to synchronize storage servers and central server with each other, I use Berkeley Algorithm. The central server polls storage servers for their time and then calculates avergae time difference between central server time and storage server's times. This difference is added to central server time to get the correct time. This correct time is used to calcuate time correction for each storage server which is then sent to each server respectively.

## Steps to Run
1. Run storageServer.py file giving command line argument for path of storage directory and port number for storage server: <br>
```python storageServer.py ./ 8082```
2. Initally run at least two storage servers.
3. Run centralServer.py file which starts the central server that normally runs on port 8080.
4. Now, you can run client.py which then asks for user ID and creates directory specific to that user for all operations.
5. To execute different operation in file system follow below format: <br>
   - List directories and files - `ls`

     ```
     ls
     ```
   - Create new directory - `create dir <path>`
     
     ```
     create dir ./newDir
     ```
   - Create new file - `create file <path>/<filename>.<extention>`

     ```
     create file ./newDir/newFile.txt
     ```
   - Write to file - `write <file path> <data>`
     ```
     write ./newDir/newFile.txt hello world!
     ```
   - Read from file - `read <file path>`
     ```
     read ./newDir/newFile.txt
     ```
   - Delete a file or directory - `delete <file path>`
     ```
     delete ./newDir/newFile.txt
     ```
   - Rename a file or directory - `rename <file path>/oldname <file path>/newname`
     ```
     rename ./newDir/newFile.txt ./newDir/newFile1.txt
     ```
