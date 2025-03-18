import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
   .book-card {
    background-color: #ffffff;
    color: #333333;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-left: 5px solid #3B82F6;
}

.book-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

.book-card strong {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1E40AF;
    display: block;
    margin-bottom: 4px;
}

.book-card em {
    font-size: 1.1rem;
    font-style: italic;
    color: #64748B;
    display: block;
    margin-bottom: 4px;
}

.book-card small {
    font-size: 1rem;
    color: #6B7280;
    display: block;
    margin-bottom: 4px;
}

.book-status {
    font-size: 1rem;
    font-weight: 500;
    padding: 6px 12px;
    border-radius: 16px;
    display: inline-block;
    margin-top: 8px;
}

.read-status {
    background-color: #d1fae5;
    color: #065f46;
}

.unread-status {
    background-color: #fde68a;
    color: #92400e;
}



</style>
""", unsafe_allow_html=True)

# Load Lottie animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load library from JSON file
def load_library():
    file_path = 'library.json'
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, 'r') as file:
                st.session_state.library = json.load(file)
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Resetting library...")
            st.session_state.library = []
            save_library()
        except Exception as e:
            st.error(f"Error loading library: {e}")
    else:
        st.session_state.library = []
        st.write("📂 No data found in library.json")  # Debug message

# Save library to JSON file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file, indent=4)
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Add a new book
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# Remove a book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        st.rerun()
# Library statistics
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        authors[book['author']] = authors.get(book['author'], 0) + 1
        
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items()))
    }

# Load library on startup
load_library()

# Sidebar navigation
st.sidebar.markdown("<h1 style='text-align: center;'>📚Navigation</h1>", unsafe_allow_html=True)
nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)

st.session_state.current_view = nav_options.lower().replace(" ", "_")

# Main UI
st.markdown("<h1 class='main-header'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

# View Library
if st.session_state.current_view == "view_library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    
    if len(st.session_state.library) == 0:
        st.warning("No books found in your library. Add some books to get started!")
    else:
        for index, book in enumerate(st.session_state.library):
            with st.container():
                st.markdown(f"""
                    <div class="book-card">
                        <strong>📖 {book['title']}</strong>  
                        <em>by {book['author']}</em>  
                        Published: {book['publication_year']}  
                        Genre: {book['genre']}  <br>
                     <div class="book-status {'read-status' if book['read_status'] else 'unread-status'}">
                     {"✅ Read" if book['read_status'] else "📌 Unread"}
                     </div>
                     </div>
                """, unsafe_allow_html=True)

                if st.button(f"Remove '{book['title']}'", key=f"remove_{index}"):
                    remove_book(index)

# Add Book
elif st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form(key='add_book_form'):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "Other"])
        read_status = st.radio("Read Status", ["Read", "Unread"])
        if st.form_submit_button("Add Book"):
            add_book(title, author, publication_year, genre, read_status == "Read")
elif st.session_state.current_view == "library_statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    stats = get_library_stats()
    st.metric("Total Books", stats['total_books'])
    st.metric("Books Read", stats['read_books'])
    st.metric("Percentage Read", f"{stats['percent_read']:.1f}%")

#Auto-refresh after adding/removing books
if st.session_state.book_added:
    st.toast("✅ Book added successfully!")
    st.session_state.book_added = False
    st.rerun()

if st.session_state.book_removed:
    st.toast("❌ Book removed successfully!")
    st.session_state.book_removed = False
    st.rerun()
