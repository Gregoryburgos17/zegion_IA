const readline = require('readline');

class Character {
  constructor(name, attack, defense, speed, specialAbility) {
    this.name = name;
    this.attack = attack;
    this.defense = defense;
    this.speed = speed;
    this.specialAbility = specialAbility;
    this.health = 100;
    this.cursedEnergy = 100;
  }

  useSpecialAbility() {
    if (this.cursedEnergy >= 30) {
      this.cursedEnergy -= 30;
      return this.specialAbility;
    }
    return null;
  }
}

const mahoraga = new Character("Mahoraga", 90, 95, 80, "Wheel of Fortune");
const sukuna = new Character("Sukuna", 95, 85, 90, "Dismantle");
const gojo = new Character("Gojo", 99, 99, 95, "Infinity");

const characters = [mahoraga, sukuna, gojo];

function calculateDamage(attacker, defender, isSpecialAbility) {
  let baseDamage = attacker.attack - defender.defense / 2;
  if (isSpecialAbility) {
    baseDamage *= 1.5;
  }
  return Math.max(0, Math.round(baseDamage + Math.random() * 10));
}

function displayStatus(character) {
  console.log(`${character.name} - Health: ${character.health}, Cursed Energy: ${character.cursedEnergy}`);
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function promptAction(character, callback) {
  console.log(`\n${character.name}'s turn:`);
  displayStatus(character);
  console.log("1. Normal Attack");
  console.log("2. Use Special Ability");
  rl.question("Choose your action (1 or 2): ", (answer) => {
    callback(answer === "2");
  });
}

function performAction(attacker, defender, useSpecialAbility) {
  const damage = calculateDamage(attacker, defender, useSpecialAbility);
  defender.health = Math.max(0, defender.health - damage);
  
  if (useSpecialAbility) {
    console.log(`${attacker.name} uses ${attacker.specialAbility} and deals ${damage} damage to ${defender.name}!`);
  } else {
    console.log(`${attacker.name} attacks ${defender.name} for ${damage} damage!`);
  }
  
  displayStatus(defender);
  
  if (defender.health <= 0) {
    console.log(`${defender.name} has been defeated!`);
    return true;
  }
  return false;
}

function aiTurn(character, target) {
  const useSpecialAbility = character.cursedEnergy >= 30 && Math.random() > 0.5;
  if (useSpecialAbility) {
    character.useSpecialAbility();
  }
  return performAction(character, target, useSpecialAbility);
}

function playerTurn(callback) {
  promptAction(characters[0], (useSpecialAbility) => {
    if (useSpecialAbility) {
      const ability = characters[0].useSpecialAbility();
      if (!ability) {
        console.log("Not enough Cursed Energy! Performing a normal attack instead.");
      }
    }
    const target = characters[1].health > 0 ? characters[1] : characters[2];
    const gameOver = performAction(characters[0], target, useSpecialAbility);
    callback(gameOver);
  });
}

function gameLoop() {
  if (characters[0].health <= 0) {
    console.log("Game Over! You have been defeated.");
    rl.close();
    return;
  }
  
  if (characters[1].health <= 0 && characters[2].health <= 0) {
    console.log("Congratulations! You have won the battle!");
    rl.close();
    return;
  }
  
  playerTurn((gameOver) => {
    if (gameOver) {
      gameLoop();
      return;
    }
    
    for (let i = 1; i < characters.length; i++) {
      if (characters[i].health > 0) {
        const target = (i === 1 || characters[0].health <= 0) ? characters[0] : characters[1];
        if (aiTurn(characters[i], target)) {
          gameLoop();
          return;
        }
      }
    }
    
    gameLoop();
  });
}

console.log("Welcome to the Jujutsu Kaisen Battle Game!");
console.log("You will play as Mahoraga. Defeat Sukuna and Gojo to win!");
gameLoop();
