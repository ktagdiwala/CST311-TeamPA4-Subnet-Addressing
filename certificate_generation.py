import subprocess

passphrase = "CST311" # Used when genereating the certs from the CSRs

# Subject line for the questions that are asked after generating the CSRs
subject = (
    "/C=US"
    "/ST=California"
    "/L=Seaside"
    "/O=CST311"
    "/OU=StackOtterflow"
    f"/CN={chat_server_name}"
)

# Function to generate the private keys for the chat server 
def genPrivateKey():
    subprocess.run(["sudo", "openssl", "genrsa", "-out", f"{chat_server_name}-key.pem", "2048"])

# Function to generate the cert signing requests for the chat server
def genCSRs():
    subprocess.run(["sudo", "openssl", "req", "-nodes", "-new", "-config", "/etc/ssl/openssl.cnf", "-key", f"{chat_server_name}-key.pem", "-out", f"{chat_server_name}.csr", "-subj", subject])

# Function to generate the certs from the CSRs generated from genCSRs for the chat server
def genCertFromCSRs():
    subprocess.run(["sudo", "openssl", "x509", "-req", "-days", "365", "-in", f"{chat_server_name}.csr", "-CA", "cacert.pem", "-CAkey", "./private/cakey.pem", "-CAcreateserial", "-out", f"{chat_server_name}.pem", "-passin", f"pass:{passphrase}"])

chat_server_name = input("Input common name of chat server: ")

# Opening the file and writing the common name of the server
with open("credentials.txt", "w") as file:
    file.write(chat_server_name)

# Writing into the hosts file the IP and common name of the chat server
# Then genreating the certificates needed
try:
    subprocess.run("sudo su")
    subprocess.run(f'echo "10.0.2.4 {chat_server_name}" >> \etc\hosts')
    genPrivateKey()
    genCSRs()
    genCertFromCSRs()
except:
    print("Error writing into /etc/hosts file")