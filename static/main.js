let board = [];
let turn = 1;
let gameOver = false;

function createCell(row, col) {
  const cell = document.createElement('div');
  cell.classList.add('cell');
  cell.dataset.col = col + 1;
  cell.onclick = () => makeMove(col + 1);
  return cell;
}

function renderBoard() {
  const boardDiv = document.getElementById('board');
  boardDiv.innerHTML = '';
  for (let row = 0; row < 6; row++) {
    for (let col = 0; col < 7; col++) {
      const cell = createCell(row, col);
      if (board[row][col] === 1) cell.classList.add('player1');
      if (board[row][col] === 2) cell.classList.add('player2');
      boardDiv.appendChild(cell);
    }
  }
}

async function startGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch('/new_game', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: 1, difficulty: parseInt(difficulty) })
  });
  const data = await res.json();
  board = data.board;
  turn = data.turn;
  gameOver = false;
  showStatusMessage('Your Turn');
  renderBoard();
  if (turn === 2) await aiPlay();
}

async function makeMove(col) {
  if (gameOver || turn !== 1) return;
  const res = await fetch('/play', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ move: col })
  });
  const data = await res.json();
  board = data.board;
  turn = data.turn;
  gameOver = data.game_over;
  renderBoard();
  if (data.winner === 1) showStatusMessage('You Win! 🎉');
  else if (data.winner === 2) showStatusMessage('Computer Wins! 😔');
  else if (!gameOver && turn === 2) {
    showStatusMessage('Computer Thinking...');
    await aiPlay();
  }
}

async function aiPlay() {
  const res = await fetch('/play', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ move: 0 })
  });
  const data = await res.json();
  board = data.board;
  turn = data.turn;
  gameOver = data.game_over;
  renderBoard();
  if (data.winner === 1) showStatusMessage('You Win! 🎉');
  else if (data.winner === 2) showStatusMessage('Computer Wins! 😔');
  else showStatusMessage('Your Turn');
}

function showStatusMessage(message) {
  const oldToast = document.getElementById("toast-message");
  if (oldToast) oldToast.remove();

  const toast = document.createElement("div");
  toast.id = "toast-message";
  toast.textContent = message;
  toast.className = "toast";

  if (message.includes("Thinking")) {
    toast.classList.add("toast-warning");
  } else if (message.includes("Wins") && message.includes("Computer")) {
    toast.classList.add("toast-danger");
  } else if (message.includes("You Win")) {
    toast.classList.add("toast-success");
  } else {
    toast.classList.add("toast-default");
  }

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}
