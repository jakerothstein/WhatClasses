import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import db_controller
import verify_email_server

app = FastAPI()
origins = [
    "http://localhost:63342",  # Update with your actual frontend URL
    "http://127.0.0.1:8000"  # Update with your FastAPI server URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/send-verify-email/{email}/{first_name}/{last_name}/{password}")
async def send_verify_email(email: str, first_name: str, last_name: str, password: str):
    if email.endswith("@stu.smuhsd.org"):
        code = db_controller.insert_random_otp(email=email, first_name=first_name, last_name=last_name,
                                               password=password)
        if code is None:
            raise HTTPException(status_code=401, detail="Email already approved")
        verify_email_server.send_verifacation_email(email=email, code=code)
        return {"message": "Email sent"}
    else:
        raise HTTPException(status_code=401, detail="Invalid email - must be @stu.smuhsd.org")


@app.get("/verify-otp/{email}/{otp}")
async def verify_otp(email: str, otp: str):
    if db_controller.verify_OTP(email=email, test_otp=otp):
        html_content = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <link rel="stylesheet" href="styles.css">
                        <title>Verification Success</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                background-color: #f0f0f0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                            }

                            .container {
                                background-color: #fff;
                                border-radius: 8px;
                                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                                padding: 20px;
                                width: 350px;
                                text-align: center;
                            }

                            h1 {
                                color: #007bff;
                            }

                            p {
                                margin: 20px 0;
                            }

                            .action-button {
                                background-color: #007bff;
                                border: none;
                                color: #fff;
                                padding: 10px;
                                border-radius: 4px;
                                cursor: pointer;
                                transition: background-color 0.3s;
                                text-decoration: none;
                            }

                            .action-button:hover {
                                background-color: #0056b3;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Verification Success</h1>
                            <p>Your account has been successfully verified.</p>
                        </div>
                    </body>
                    </html>

                    """
        db_controller.create_user(email=email)
        db_controller.clear_otp(email=email)
        return HTMLResponse(content=html_content, status_code=200)
    else:
        raise HTTPException(status_code=402, detail="Invalid OTP")


@app.get("/get-courses/")
async def get_courses():
    return db_controller.get_courses()


@app.get("/login/{email}/{password}")
async def login(email: str, password: str):
    response = db_controller.login(email=email, password=password)
    if response is not False:
        return response
    else:
        raise HTTPException(status_code=401, detail="Login failed")


class Classes(BaseModel):
    class_list: list


# https://docs.google.com/document/d/1gYqJdNZp55tprsbdqLgaPTkau5-nfGVBAkQk1t2gMO4/edit
@app.post("/log-classes/{email}/{token}")
async def log_classes(email: str, token: str, classes: Classes):  # find out how to get list
    class_list = classes.dict()['class_list']
    if db_controller.check_token(email=email, token=token):
        db_controller.add_user_courses(email=email, classes=class_list)
        return {"message": "Courses logged"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/logout/{email}/{token}")
async def logout(email: str, token: str):
    if db_controller.check_token(email=email, token=token):
        db_controller.logout(email=email)
        return {"message": "Logged out"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/get-classmates/{email}/{token}")
async def get_classmates(email: str, token: str):
    if db_controller.check_token(email=email, token=token):
        return db_controller.get_classmates(email=email)
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/reset-password_email/{email}")
async def reset_password(email: str):
    if db_controller.check_email(email=email):
        otp = db_controller.new_otp(email=email)
        if otp is None:
            raise HTTPException(status_code=401, detail="Email not approved")
        verify_email_server.reset_password_email(email=email, code=otp)
        return {"message": "Password reset email sent"}
    else:
        raise HTTPException(status_code=401, detail="Invalid email")


@app.get("/reset-password/{email}/{otp}")
async def reset_password(email: str, otp: str):
    if db_controller.verify_OTP(email=email, test_otp=otp):
        html_content = """
           <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="styles.css">
                <title>Password Reset</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f0f0f0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }}

                    .container {{
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                        padding: 20px;
                        width: 350px;
                        text-align: center;
                    }}

                    h1 {{
                        color: #007bff;
                    }}

                    form {{
                        text-align: left;
                        margin-top: 20px;
                    }}

                    label {{
                        font-weight: bold;
                    }}

                    input {{
                        display: block;
                        width: 100%;
                        padding: 10px;
                        margin-bottom: 10px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }}

                    /* Adjust the width of the input fields */
                    #new_password, #confirm_password {{
                        width: 100%;
                        max-width: 250px; /* You can adjust this value as needed */
                    }}

                    button {{
                        background-color: #007bff;
                        border: none;
                        color: #fff;
                        padding: 10px;
                        border-radius: 4px;
                        cursor: pointer;
                        transition: background-color 0.3s;
                    }}

                    button:hover {{
                        background-color: #0056b3;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Password Reset</h1>
                    <form action="/perform-reset" method="post">
                        <input type="hidden" name="email" value="{}">
                        <label for="new_password">New Password:</label>
                        <input type="password" id="new_password" name="new_password" required>
                        <label for="confirm_password">Confirm Password:</label>
                        <input type="password" id="confirm_password" name="confirm_password" required>
                        <button type="submit">Reset Password</button>
                    </form>
                </div>
            </body>
            </html>
        """.format(email)
        return HTMLResponse(content=html_content, status_code=200)
    else:
        raise HTTPException(status_code=402, detail="Invalid OTP")


@app.post("/perform-reset")
async def perform_reset(
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        email: str = Form(...)
):
    if db_controller.verify_OTP(email=email, test_otp=None):
        raise HTTPException(status_code=401, detail="OTP not verified")
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Perform password reset logic here, e.g., update the user's password in the database
    db_controller.update_user_password(email=email, new_password=new_password)

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="styles.css">
    <title>Password Changed</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .container {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 350px;
            text-align: center;
        }

        h1 {
            color: #007bff;
        }

        p {
            margin: 20px 0;
        }

        .action-button {
            background-color: #007bff;
            border: none;
            color: #fff;
            padding: 10px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
            text-decoration: none;
        }

        .action-button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Password Changed</h1>
        <p>Your account password has been successfully changed.</p>
    </div>
</body>
</html>

    """
    db_controller.clear_otp(email=email)
    return HTMLResponse(content=html_content, status_code=200)


def dump_courses():
    courses_data = [
        ("Math", "Algebra 1", "?", "alg1"),
        ("Math", "Geometry", "?", "geometry"),
        ("Math", "Integrated Mathematics II", "?", "integ2"),
        ("Math", "Algebra 2", "?", "alg2"),
        ("Math", "Data Science", "?", "datasci"),
        ("Math", "Comp Math1", "?", "comp1"),
        ("Math", "Comp Math2", "?", "comp2"),
        ("Math", "Finite Math and Statistics", "?", "finite"),
        ("Math", "Pre-Calculus", "?", "precalc"),
        ("Math", "AP Calculus AB", "?", "calc_ab"),
        ("Math", "AP Calculus BC", "?", "calc_bc"),
        ("Math", "AP Statistics", "?", "ap_stats"),
        ("Math", "AP Compsci", "?", "ap_cs"),

        ("English", "English I", "?", ""),
        ("English", "English II", "?", ""),
        ("English", "English II Advanced Standing (AS)", "?", ""),
        ("English", "English III", "?", ""),
        ("English", "AP English Language and Composition", "?", ""),
        ("English", "English IV", "?", ""),
        ("English", "AP English Literature and Composition", "?", ""),

        ("Physical Education", "PE 1", "?", "pe1"),
        ("Physical Education", "PE 2", "?", "pe2"),

        ("Science", "Biology, the Living Earth ", "?", "cp_bio"),
        ("Science", "AP Biology", "?", "ap_bio"),
        ("Science", "Chemistry in the Earth System", "?", "cp_chem"),
        ("Science", "AP Chemistry", "?", "ap_chem"),
        ("Science", "Environmental Science", "?", "cp_es"),
        ("Science", "AP Environmental Science", "?", "ap_es"),
        ("Science", "Physics in the Universe", "?", "cp_physics"),
        ("Science", "AP Physics 1", "?", "ap_physics"),

        ("Social Science", "Introduction to Ethnic Studies", "?", "eths"),
        ("Social Science", "Modern World History", "?", "cp_wh"),
        ("Social Science", "AP World History: Modern", "?", "ap_wh"),
        ("Social Science", "United States History", "?", "cp_ush"),
        ("Social Science", "AP United States History", "?", "ap_ush"),
        ("Social Science", "American Government", "?", "cp_gov"),
        ("Social Science", "AP US Government & Politics", "?", "ap_gov"),
        ("Social Science", "Economics", "?", "cp_econ"),
        ("Social Science", "AP Macroeconomics", "?", "ap_econ"),

        ("World Language", "Chinese I", "?", "chin1"),
        ("World Language", "Chinese II", "?", "chin2"),
        ("World Language", "Chinese III", "?", "chin3"),
        ("World Language", "Chinese IV Honors", "?", "chin4"),
        ("World Language", "Italian I", "?", "ital1"),
        ("World Language", "Italian II", "?", "ital2"),
        ("World Language", "Italian III", "?", "ital3"),
        ("World Language", "AP Italian Language and Culture", "?", "ap_ital"),
        ("World Language", "Spanish I", "?", "span1"),
        ("World Language", "Spanish II", "?", "span2"),
        ("World Language", "Spanish III", "?", "span3"),
        ("World Language", "Spanish for Native Speakers (III)", "?", "span3_native"),
        ("World Language", "Spanish IV Honors", "?", "span4"),
        ("World Language", "AP Spanish Language & Culture", "?", "ap_spanlang"),
        ("World Language", "AP Spanish Literature & Culture", "?", "ap_spanlit"),

        ("Electives", "Introduction to Business (BUS 100)", "?", ""),
        ("Electives", "Creativity And Innovation In Entrepreneurship (BUS 161)", "?", ""),
        ("Electives", "AVID", "?", ""),
        ("Electives", "Guided Studies", "?", ""),
        ("Electives", "Academic Peer Tutoring", "?", ""),
        ("Electives", "Leadership", "?", ""),
        ("Electives", "Service Commission", "?", ""),
        ("Electives", "Teacher/Office Aide (TA)", "?", ""),
        ("Electives", "Directed Studies", "?", ""),
        ("Electives", "Facing History and Ourselves", "?", ""),
        ("Electives", "Psychology", "?", ""),
        ("Electives", "Introduction to Yoga", "?", ""),
        ("Electives", "Weight & Fitness Training", "?", ""),
        ("Electives", "Health", "?", ""),
        ("Electives", "Cinema & Society", "?", ""),
        ("Electives", "Speech", "?", ""),

        ("Visual & Performing Arts (VPA)", "Art", "?", ""),
        ("Visual & Performing Arts (VPA)", "Art Advanced", "?", ""),
        ("Visual & Performing Arts (VPA)", "Ceramics", "?", ""),
        ("Visual & Performing Arts (VPA)", "Ceramics Advanced", "?", ""),
        ("Visual & Performing Arts (VPA)", "3D Game Art & Design", "?", ""),
        ("Visual & Performing Arts (VPA)", "3D Game Art & Design Advanced", "?", ""),
        ("Visual & Performing Arts (VPA)", "AP Studio Art", "?", ""),
        ("Visual & Performing Arts (VPA)", "Drama", "?", ""),
        ("Visual & Performing Arts (VPA)", "Drama Advanced", "?", ""),
        ("Visual & Performing Arts (VPA)", "Concert Band", "?", ""),
        ("Visual & Performing Arts (VPA)", "Wind Ensemble", "?", ""),
        ("Visual & Performing Arts (VPA)", "Jazz Ensemble", "?", ""),
        ("Visual & Performing Arts (VPA)", "Chorus", "?", ""),
        ("Visual & Performing Arts (VPA)", "Concert Choir", "?", ""),
        ("Visual & Performing Arts (VPA)", "Chamber Singers", "?", ""),

        ("CTE", "Career Planning & Life Exploration (CRER 100)", "?", ""),
        ("CTE", "Architectural Design I", "?", ""),
        ("CTE", "Architectural Design II", "?", ""),
        ("CTE", "Art of Video", "?", ""),
        ("CTE", "Art of Video Advanced", "?", ""),
        ("CTE", "Digital Photography", "?", ""),
        ("CTE", "Engineering Technology", "?", ""),
        ("CTE", "Foods & Nutrition", "?", ""),
        ("CTE", "Culinary Arts", "?", ""),
        ("CTE", "Journalism", "?", ""),
        ("CTE", "Journalism Advanced", "?", ""),
        ("CTE", "Publications", "?", ""),
        ("CTE", "Adv Publications", "?", ""),
        ("CTE", "Principles of Computer Science", "?", "")
]

    # Insert example course data
    for course in courses_data:
        db_controller.insert_course(*course)

dump_courses()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="path_to_private_key.key", ssl_certfile="path_to_certificate.crt")