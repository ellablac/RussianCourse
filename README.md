The site is published at https://ellablac.github.io/RussianCourse/

# Community Russian Language Course

## Overview

This is a beginner-friendly Russian language course designed for English speakers. The course assumes no prior knowledge of Russian and gradually progresses to more advanced topics. It is community-oriented, aiming to help participants break language barriers, especially in social settings.

## Structure

* **Home Page**: Introduction and navigation menu.
* **Lessons Page**: Contains a list of lessons, each linking to its own dedicated page.

  * Introduction
  * Lesson 1

    * Alphabet
    * Practice Worksheets
    * Alphabet Game
  * Lesson 2
  * Lesson 3
  * Lesson 4
  * Lesson 5
* **Resources Page**: Contains supporting materials such as audio, images, and utilities.

## File Organization

* **assets/**: files such as css, js, mp3, jpg that are used in more than one lessons
  * css/
    * alphabet.css
    * animations.css
    * gradients.css
    * site.css
  * html/
    * navbar.html
  * js/
    * audioUtils.js
    * navbar.js
    * site-search.js
  * json/
    * search-index.json
  * sound/ All sound files go here, even if used in one lesson only
    * female/
      * [mp3's with female voice of sounds related to alphabet]
    * male/
      * [mp3's with male voice of sounds related to alphabet]
      * words/
        * [mp3's with male voice of words and sentences]

* **lesson1/**
  * assets/
    * [images for this lesson]
  * letters/
    * l_17.html: utility html that plays a video and syncs with a separate audio
  * [all html files for lesson 1]

* **lesson2/**
  * genders.html
  * key_diff.html

* **pdf/**
  * lesson 1/
    * [pdf files]

* **resources/**
  * [html files used in the Resources page]

* **utilities/**: helper functions, tools.
  * generate_sitemap.py
  * text2speech.html
  * word2mp3.py: convert text to speech

* index.html: Home page.
* introduction.html
* lessons.html
* README.md
* requirements.txt
* sitemap.xml
* techniques.html

## Development
* To run python scripts, activate venv: source .venv/bin/activate
* Run: python utilities/word2mp3.py

## Technologies

* HTML5
* CSS3
* JavaScript
* Bootstrap
* Python

## Deployment

The course materials will be hosted on GitHub Pages for easy access.

### Steps for publishing the site:

1. Push repository to GitHub.
2. Enable GitHub Pages under repository settings.
3. Access the site at `https://username.github.io/repository-name`.

### 
