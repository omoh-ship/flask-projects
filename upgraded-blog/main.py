from flask import Flask, render_template, request
import requests
import smtplib

MY_EMAIL = "EMAIL"
MY_PASSWORD = "EMAIL_PASSWORD"

all_posts = requests.get("https://api.npoint.io/59c7c056a375ddaf1959").json()

app = Flask(__name__)


def send_email(name, email, num, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs="gloriaisedu@gmail.com",
            msg=f"Subject: New message from blog\n\n{message}\nFrom Name:{name}\nEmail: {email}\nPhone number: {num}"
        )


@app.route('/')
def index():
    return render_template('index.html', blog_posts=all_posts)


@app.route('/about')
def about_me():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact_me():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        num = request.form['phone_num']
        message = request.form['message']
        send_email(name, email, num, message)

        return render_template('contact.html', msg_sent=True)
    return render_template('contact.html', msg_sent=False)


@app.route('/post/<int:blog_id>')
def posty(blog_id):
    current_post = all_posts[blog_id - 1]
    return render_template('post.html', post=current_post)


if __name__ == "__main__":
    app.run(debug=True)
