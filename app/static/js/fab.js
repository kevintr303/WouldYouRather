document.addEventListener('DOMContentLoaded', () => {
    const fabToggleButton = document.getElementById('fab-toggle');
    const fabContainer = document.querySelector('.fab-container');
    const fabIcon = document.getElementById('fab-icon');
    const fabAddButton = document.getElementById('fab-add');
    const fabStatsButton = document.getElementById('fab-stats');
    const fabAboutButton = document.getElementById('fab-about');

    const askModal = document.getElementById('ask-modal');
    const statsModal = document.getElementById('stats-modal');
    const aboutModal = document.getElementById('about-modal');

    const fabSearchButton = document.getElementById('fab-search');
    const searchModal = document.getElementById('search-modal');

    fabToggleButton.addEventListener('click', () => {
        fabContainer.classList.toggle('open');
        fabIcon.style.transform = fabContainer.classList.contains('open') ? 'rotate(45deg)' : 'rotate(0deg)';
    });

    fabAddButton.addEventListener('click', () => {
        openModal(askModal);
    });

    fabStatsButton.addEventListener('click', () => {
        openModal(statsModal);
    });

    fabAboutButton.addEventListener('click', () => {
        openModal(aboutModal);
    });

    fabSearchButton.addEventListener('click', () => {
        openModal(searchModal);
        setTimeout(() => {
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }, 100);
    });

    function openModal(modal) {
        if (!modal) return;
        const modalContent = modal.querySelector('.modal-content');
        modal.classList.remove('hidden');
        modalContent.classList.add('modal-fade-in');
        fabContainer.classList.remove('open');
        fabIcon.style.transform = 'rotate(0deg)';
    }

    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', (event) => {
            const modal = event.target.closest('.modal');
            closeModal(modal);
        });
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    function closeModal(modal) {
        if (!modal) return;
        const modalContent = modal.querySelector('.modal-content');
        modalContent.classList.remove('modal-fade-in');
        modalContent.classList.add('modal-fade-out');
        setTimeout(() => {
            modal.classList.add('hidden');
            modalContent.classList.remove('modal-fade-out');
        }, 300);
    }

    document.addEventListener('keydown', function (event) {
        if (event.key === '/' && !event.target.matches('input, textarea')) {
            event.preventDefault();
            openModal(searchModal);
            setTimeout(() => {
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }, 100);
        }

        if (event.key === 'Escape') {
            const activeModal = document.querySelector('.modal:not(.hidden)');
            if (activeModal) {
                closeModal(activeModal);
            }
        }
    });
});
