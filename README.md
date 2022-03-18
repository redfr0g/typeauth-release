![typeauth-logo](./static/img/typeauth-logo.png)
# typeauth

### tl;dr
Typeauth adds biometric security to authentication based on user typing style during login phase. It was created as PoC (*Proof of concept*) tool to present and study keystroke biometrics authentication with various typing languages.

## Description
This project was created to aid the research for masters thesis at Warsaw University of Technology. The goal of the project was to study the impact of the typing language characteristics on overall system effectiveness. More detailed writeup of the research can be found [here](https://github.com/redfr0g/typeauth-release/blob/main/typeauth_thesis.pdf).

## How it works
The application uses JS frontend to record users keystroke timing data during registration phase. Than this data is converted to a unique user chracteristic vector and saved to the database next to the password and login. When user tries to log in the biometrics act as a 2nd factor authentication (2FA). After retyping a randomly generated phase the same timing data is send to the backend to be classified. Typeauth uses two different classifiers to identify users:
- Manhattan distance classifier (less effective)
- SVM classifier (more effective)
Based on the result from the classifier the user is either authenticated or not.

## Research
Feel free to use this application in Your research but if You do, make sure You cite this paper:

- Jakub Brzozowski, _"Typeauth - enhancing the efficiency of keystroke biometrics in context of the typing language"_, 2022

More languages and words can be added to the generator by modyfing the `generator.py` file. For now the application only supports the following sentence geration modes:
- Short words 🇬🇧
- Long words 🇬🇧
- Short words 🇵🇱
- Long words 🇵🇱

## Installation
1. Clone this git repository
2. Install dependencies using `pip install -r requirements.txt`
3. Run the applicatoin with `python typeauth.py`
4. Go to `http://127.0.0.1:5000` to access the application

## Demo
Demo application can be accessed at `http://www.typeauth.com` (email me for credentials jakub(at)brzozowski.io).
