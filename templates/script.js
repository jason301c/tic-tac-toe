document.getElementById('start-game').addEventListener('click', function() {
    // Generate a unique game ID
    const gameId = Math.random().toString(36).substring(2, 15);
    const gameLink = `${window.location.href}game.html?gameId=${gameId}`;
    
    // Display the game link
    document.getElementById('link-container').style.display = 'block';
    document.getElementById('game-link').value = gameLink;
});
