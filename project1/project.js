// Global Variables
let currentMode = null;
let isListening = false;
let recognition;
let isChatbotOpen = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize Web Speech API if available
  initializeSpeechRecognition();
  
  // Set up event listeners
  setupEventListeners();
  
  // Show mental health mode by default
  setTimeout(() => {
    showFeature('mental');
  }, 500);
});

function initializeSpeechRecognition() {
  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = function() {
      isListening = true;
      updateVoiceUI();
    };
    
    recognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript;
      processVoiceInput(transcript);
    };
    
    recognition.onerror = function(event) {
      console.error('Speech recognition error', event.error);
      displayMessage("Sorry, I didn't catch that. Could you try again?", 'ai');
      isListening = false;
      updateVoiceUI();
    };
    
    recognition.onend = function() {
      isListening = false;
      updateVoiceUI();
    };
  } else {
    document.getElementById('voiceToggle').disabled = true;
    document.getElementById('voiceToggle').innerHTML = '<i class="fas fa-microphone-slash"></i> Voice Not Supported';
    document.getElementById('voice-input-btn').style.display = 'none';
  }
}

function setupEventListeners() {
  // Voice toggle button
  document.getElementById('voiceToggle').addEventListener('click', toggleVoiceRecognition);
  
  // Voice input button in chat
  document.getElementById('voice-input-btn').addEventListener('click', toggleVoiceRecognition);
  
  // Text input handling
  document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      handleUserInput();
    }
  });
  
  // Chatbot close button
  document.querySelector('.close-chat').addEventListener('click', toggleChatbot);
}

function toggleVoiceRecognition() {
  if (!recognition) return;
  
  if (isListening) {
    recognition.stop();
  } else {
    try {
      recognition.start();
      displayMessage("I'm listening...", 'ai');
    } catch (e) {
      console.error("Speech recognition error:", e);
      displayMessage("Voice recognition failed. Please try again.", 'ai');
    }
  }
}

function updateVoiceUI() {
  const voiceBtn = document.getElementById('voiceToggle');
  const statusIndicator = document.getElementById('voice-status');
  const voiceInputBtn = document.getElementById('voice-input-btn');
  
  if (isListening) {
    voiceBtn.classList.add('listening');
    voiceBtn.innerHTML = '<i class="fas fa-microphone"></i> Listening...';
    statusIndicator.style.display = 'block';
    voiceInputBtn.innerHTML = '<i class="fas fa-stop"></i>';
    voiceInputBtn.style.backgroundColor = 'var(--danger-color)';
  } else {
    voiceBtn.classList.remove('listening');
    voiceBtn.innerHTML = '<i class="fas fa-microphone"></i> Tap to Speak';
    statusIndicator.style.display = 'none';
    voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    voiceInputBtn.style.backgroundColor = 'var(--accent-color)';
  }
}

function showFeature(type) {
  currentMode = type;
  const title = document.getElementById('feature-title');
  const desc = document.getElementById('feature-description');
  const featureBox = document.getElementById('feature-box');
  const chatbot = document.getElementById('chatbot');
  
  // Reset active state on buttons
  document.querySelectorAll('nav button').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Set active state on clicked button
  event.target.classList.add('active');
  
  // Hide elements with fade-out effect
  featureBox.style.opacity = '0';
  chatbot.style.opacity = '0';
  
  setTimeout(() => {
    // Update content based on selected feature
    switch(type) {
      case 'mental':
        title.textContent = "Mental Health Companion";
        desc.textContent = "EVA listens to your voice, detects emotional cues, and provides empathetic support including breathing exercises, mood tracking, and comforting responses.";
        break;
      case 'daily':
        title.textContent = "Daily Productivity Assistant";
        desc.textContent = "Get weather updates, manage your schedule, set reminders, and stay organized with EVA's intelligent daily assistance features.";
        break;
      case 'support':
        title.textContent = "Smart Customer Support";
        desc.textContent = "EVA acts as your first-line support agent, answering FAQs, troubleshooting issues, and escalating complex queries when needed.";
        break;
    }
    
    // Show elements with fade-in effect
    featureBox.style.opacity = '1';
    featureBox.classList.add('visible');
    
    // Initialize chat for this mode
    initializeChat(type);
    
    // Open chatbot by default
    toggleChatbot(true);
  }, 300);
}

function initializeChat(feature) {
  const chatbox = document.getElementById('chatbox');
  chatbox.innerHTML = '';
  
  let initialMessage = '';
  switch(feature) {
    case 'mental':
      initialMessage = "Hello there! I'm EVA, your mental health companion. How are you feeling today?";
      break;
    case 'daily':
      initialMessage = "Good day! I'm here to help with your daily tasks. What can I assist you with?";
      break;
    case 'support':
      initialMessage = "Welcome to support! How may I assist you today?";
      break;
  }
  
  // Display initial message with typing effect
  typeMessage(initialMessage, 'ai');
}

function toggleChatbot(forceOpen = false) {
  const chatbot = document.getElementById('chatbot');
  
  if (forceOpen) {
    isChatbotOpen = true;
    chatbot.style.display = 'block';
    setTimeout(() => {
      chatbot.classList.add('visible');
    }, 10);
    return;
  }
  
  isChatbotOpen = !isChatbotOpen;
  
  if (isChatbotOpen) {
    chatbot.style.display = 'block';
    setTimeout(() => {
      chatbot.classList.add('visible');
    }, 10);
  } else {
    chatbot.classList.remove('visible');
    setTimeout(() => {
      chatbot.style.display = 'none';
    }, 300);
  }
}

function handleUserInput() {
  const userInput = document.getElementById('user-input').value.trim();
  if (userInput === "") return;
  
  // Display User's Message
  displayMessage(userInput, 'user');
  
  // Clear input field
  document.getElementById('user-input').value = '';
  
  // Process input and generate response
  processUserInput(userInput);
}

function processVoiceInput(transcript) {
  // Display User's Message
  displayMessage(transcript, 'user');
  
  // Process input and generate response
  processUserInput(transcript);
}

function processUserInput(input) {
  // Show typing indicator
  showTypingIndicator();
  
  // Simulate processing delay
  setTimeout(() => {
    // Hide typing indicator
    hideTypingIndicator();
    
    // Generate response based on mode and input
    const response = generateResponse(input);
    
    // Display AI's response with typing effect
    typeMessage(response, 'ai');
  }, 1000 + Math.random() * 1000);
}

function generateResponse(input) {
  input = input.toLowerCase();
  let response = "I'm still learning. Could you rephrase that or ask something else?";
  
  if (!currentMode) return response;
  
  switch(currentMode) {
    case 'mental':
      if (input.includes('sad') || input.includes('depressed') || input.includes('unhappy')) {
        response = "I'm sorry you're feeling this way. Remember that it's okay to feel sad sometimes. Would you like to try a quick breathing exercise to help?";
      } else if (input.includes('happy') || input.includes('good') || input.includes('great')) {
        response = "That's wonderful to hear! Can you tell me more about what's making you happy?";
      } else if (input.includes('anxious') || input.includes('nervous') || input.includes('stressed')) {
        response = "Anxiety can be challenging. Let's try the 4-7-8 breathing technique: Breathe in for 4 seconds, hold for 7, exhale for 8. Ready to try?";
      } else if (input.includes('exercise') || input.includes('breathing')) {
        response = "Great! Let's do a simple exercise: Breathe in deeply for 4 seconds, hold for 4, and exhale for 6. Repeat 3 times. I'll guide you through it.";
      } else {
        response = "I'm here to listen. Would you like to share more about how you're feeling or try a mindfulness exercise?";
      }
      break;
      
    case 'daily':
      if (input.includes('weather')) {
        response = "I can check the weather for you. For accurate results, I'll need to know your location. Would you like to set your location now?";
      } else if (input.includes('remind') || input.includes('reminder')) {
        response = "I can set reminders for you. Please tell me what you'd like to be reminded about and when (e.g., 'Call mom at 5pm tomorrow').";
      } else if (input.includes('schedule') || input.includes('calendar')) {
        response = "I can help manage your schedule. Would you like to add an event, check your calendar, or something else?";
      } else if (input.includes('time')) {
        response = `The current time is ${new Date().toLocaleTimeString()}`;
    } else {
        response = "I can help with weather, reminders, scheduling, and more. What specifically would you like assistance with?";
      }
      break;
      
    case 'support':
      if (input.includes('problem') || input.includes('issue') || input.includes('trouble')) {
        response = "I'm sorry you're experiencing this issue. Could you describe the problem in more detail so I can help better?";
      } else if (input.includes('account') || input.includes('login')) {
        response = "For account issues, I can help reset your password or connect you with our support team. Would you like to reset your password now?";
      } else if (input.includes('payment') || input.includes('bill')) {
        response = "I can assist with payment questions. Are you having trouble with a recent charge, or do you need help updating payment information?";
      } else if (input.includes('contact') || input.includes('human') || input.includes('agent')) {
        response = "I can connect you with a human agent. Please hold while I transfer you... (This would connect to live support in a real implementation)";
      } else {
        response = "I'm here to help with your questions. Could you tell me more about what you need assistance with?";
      }
      break;
  }
  
  return response;
}

function displayMessage(message, sender) {
  const chatbox = document.getElementById('chatbox');
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('chat-message', sender);
  messageDiv.textContent = message;
  chatbox.appendChild(messageDiv);
  chatbox.scrollTop = chatbox.scrollHeight;
}

function typeMessage(message, sender) {
  const chatbox = document.getElementById('chatbox');
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('chat-message', sender);
  chatbox.appendChild(messageDiv);
  
  let i = 0;
  const typingSpeed = 20 + Math.random() * 10; // Vary speed slightly
  
  function type() {
    if (i < message.length) {
      messageDiv.textContent += message.charAt(i);
      i++;
      chatbox.scrollTop = chatbox.scrollHeight;
      setTimeout(type, typingSpeed);
    }
  }
  
  type();
}

function showTypingIndicator() {
  const chatbox = document.getElementById('chatbox');
  const typingDiv = document.createElement('div');
  typingDiv.classList.add('typing-indicator');
  typingDiv.id = 'typing-indicator';
  
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('div');
    dot.classList.add('typing-dot');
    typingDiv.appendChild(dot);
  }
  
  chatbox.appendChild(typingDiv);
  chatbox.scrollTop = chatbox.scrollHeight;
}

function hideTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}
