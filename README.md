# WhatClasses
Web app to see what classes you have in common with other students!

# Features
> Log classes and see what classes you have with other students in the database
> Working email server to send emails to verify email addresses

# Setup
- In all HTML files, verify_email_server.py and main.py change the url_base and origin (for main.py) to the base of wherever you are hosting the fastapi server
- When you run the program, it will automatically create a database, and if the dump_courses() function is run, it will input the classes in the dump_courses function into the database. The format for adding tuples is (Course Category (Math), Course Name (Algebra II), Teacher Name (Jim Harris), Course ID (ap_spanlang))
- In verify_email_server.py, change the password and sender email and password to your email and password of your email that will be sending verification requests. I recommend using an [app password](https://support.google.com/accounts/answer/185833?hl=en)

# Photos
![image](https://github.com/jakerothstein/WhatClasses/assets/73565590/69651d9f-97e0-47af-9021-e8ba0e1f9826)
> Example Login

![image](https://github.com/jakerothstein/WhatClasses/assets/73565590/0d71ae2b-8723-441d-b879-eeca93b38494)
> Class logging example

![image](https://github.com/jakerothstein/WhatClasses/assets/73565590/e19fda17-ece1-4616-8ec3-3823c7178824)
> Example dashboard

![image](https://github.com/jakerothstein/WhatClasses/assets/73565590/f14a049d-c19a-4afd-8127-bccde5e2fd89)
> Example OTP email

# Credits
Developed by Jake Rothstein and Minjun Kim 
> Development time: 2 days 
