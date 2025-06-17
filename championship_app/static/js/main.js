const menuButtons = document.querySelectorAll('.menu-item');
const mainContent = document.querySelector('main');
let file = 'html/home.html';

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.menu-item').forEach(button => {
            const annotation = document.createElement('span');
            annotation.className = 'annotation';
            annotation.textContent = button.title;
            button.appendChild(annotation);
    });

    fetch(file)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            mainContent.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading content:', error);
            mainContent.innerHTML = '<p>Error loading content.</p>';
        });
});

menuButtons.forEach(button => {
    button.addEventListener('click', () => {
        menuButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        switch (button.title) {
            case 'Home':
                file = 'html/home.html';
                break;
            case 'New Championship':
                file = 'html/new_champ.html';
                break;
            case 'Existing Championships':
                file = 'html/champs.html';
                break;
            case 'Car & Track Settings':
                file = 'html/ct_settings.html';
                break;
            case 'App Settings':
                file = 'html/settings.html';
                break;
            default:
                file = 'html/home.html';
        }

        fetch(file)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(html => {
                mainContent.innerHTML = html;
            })
            .catch(error => {
                console.error('Error loading content:', error);
                mainContent.innerHTML = '<p>Error loading content.</p>';
            });
    });
});