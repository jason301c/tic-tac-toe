document.getElementById('start-game').addEventListener('click', function() {
    fetch('/create-game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
      .then(data => {
        if (data.status === 'Game created!') {
            const gameLink = `${window.location.origin}/game/${data.gameId}`;
            const linkContainer = document.getElementById('link-container');
            const gameLinkInput = document.getElementById('game-link');

            gameLinkInput.value = gameLink;
            linkContainer.style.display = 'block';
        }
      });
});

document.getElementById('copy-link').addEventListener('click', function() {
    const gameLinkInput = document.getElementById('game-link');
    gameLinkInput.select();
    document.execCommand('copy');
    alert('Link copied to clipboard!');
});

document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const winnerMessageElement = document.getElementById('winner-message');
    const gameId = window.location.pathname.split('/').pop();
    let currentPlayer = 'X';

    function handleClick(e) {
        const cell = e.target;
        const index = Array.from(cells).indexOf(cell);

        fetch('/make-move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ gameId: gameId, index: index, player: currentPlayer })
        }).then(response => response.json())
          .then(data => {
            if (data.status === 'Move made') {
                cell.innerText = currentPlayer;
                currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
            } else if (data.status === 'Player won' || data.status === 'Draw') {
                winnerMessageElement.innerText = data.status === 'Player won' ? `${currentPlayer} wins!` : 'Draw!';
                winnerMessageElement.style.display = 'block';
                cells.forEach(cell => cell.removeEventListener('click', handleClick));
            }
          });
    }

    cells.forEach(cell => {
        cell.addEventListener('click', handleClick, { once: true });
    });
});
