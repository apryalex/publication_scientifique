from flask import Flask, render_template, request, redirect, url_for
from flask_paginate import Pagination, get_page_args
from data import DBManager
from datetime import datetime

app = Flask(__name__)

db_manager = DBManager('mongodb://root:example@mongodb:27017/', 'DBLP', 'publis')

@app.route('/')
@app.route('/page_<int:page>')
def index(page=1):
    per_page = 10  # Number of publications per page
    offset = (page - 1) * per_page
    total = db_manager.get_publication_count()
    publications = db_manager.get_publications(offset, per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    return render_template('index.html', publications=publications, pagination=pagination)

@app.route('/filter_author', methods=['GET', 'POST'])
def filter_author():
    if request.method == 'POST':
        author = request.form['author']
        filtered_publications = db_manager.get_publications_by_author(author)
        return render_template('filtered_publications.html', publications=filtered_publications)

    authors = db_manager.get_authors()
    return render_template('filter_author.html', authors=authors)

@app.route('/filter_date', methods=['GET', 'POST'])
def filter_date():
    if request.method == 'POST':
        start_date = int(request.form['start_date'])
        filtered_publications = db_manager.get_publications_by_date(start_date)
        return render_template('filtered_publications.html', publications=filtered_publications)

    return render_template('filter_date.html')

@app.route('/publication/<publication_id>')
def publication_details(publication_id):
    publication = db_manager.get_publication_by_id(publication_id)
    return render_template('publication_details.html', publication=publication)

@app.route('/add_publication', methods=['GET', 'POST'])
def add_publication():
    if request.method == 'POST':
        data = {
            "_id": request.form['id'],
            "type": request.form['type'],
            "title": request.form['title'],
            "pages": {"start": int(request.form['start_page']), "end": int(request.form['end_page'])},
            "year": int(request.form['year']),
            "booktitle": request.form['booktitle'],
            "url": request.form['url'],
            "authors": [author.strip() for author in request.form['authors'].split(',')]
        }
        db_manager.add_publication(data)
        return redirect(url_for('index'))

    return render_template('add_publication.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
