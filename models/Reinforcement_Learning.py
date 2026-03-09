"""
Reinforcement Learning Models
Implementation of algorithms for learning through interaction with environments
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional, Dict, Any, Callable
import matplotlib.pyplot as plt
from collections import defaultdict, deque
import random
import logging
from abc import ABC, abstractmethod
import gym
from gym import spaces
import time

logger = logging.getLogger(__name__)


class QLearning:
    """
    Q-Learning algorithm for reinforcement learning
    """

    def __init__(self, n_states: int, n_actions: int, learning_rate: float = 0.1,
                 discount_factor: float = 0.9, epsilon: float = 1.0,
                 epsilon_decay: float = 0.995, epsilon_min: float = 0.01):
        self.n_states = n_states
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Initialize Q-table
        self.q_table = np.zeros((n_states, n_actions))

        self.is_fitted = False
        self.training_history = []

    def get_action(self, state: int, training: bool = True) -> int:
        """Get action using epsilon-greedy policy"""
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)  # Explore
        else:
            return np.argmax(self.q_table[state])  # Exploit

    def update_q_value(self, state: int, action: int, reward: float, next_state: int):
        """Update Q-value using Q-learning update rule"""
        # Q(s,a) = Q(s,a) + α[r + γ * max(Q(s',a')) - Q(s,a)]
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state, action] = new_q

    def decay_epsilon(self):
        """Decay epsilon for exploration-exploitation trade-off"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def train(self, env, n_episodes: int = 1000, max_steps_per_episode: int = 100,
              verbose: bool = False) -> List[float]:
        """Train the Q-learning agent"""
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            total_reward = 0
            done = False
            steps = 0

            while not done and steps < max_steps_per_episode:
                action = self.get_action(state, training=True)
                next_state, reward, done, info = env.step(action)

                self.update_q_value(state, action, reward, next_state)

                state = next_state
                total_reward += reward
                steps += 1

            # Decay epsilon
            self.decay_epsilon()

            episode_rewards.append(total_reward)
            self.training_history.append(total_reward)

            if verbose and (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{n_episodes}, "
                      f"Average Reward: {np.mean(episode_rewards[-100:]):.2f}, "
                      f"Epsilon: {self.epsilon:.3f}")

        self.is_fitted = True
        return episode_rewards

    def predict(self, state: int) -> int:
        """Get best action for given state (exploitation only)"""
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        return np.argmax(self.q_table[state])

    def get_policy(self) -> np.ndarray:
        """Get the learned policy (best action for each state)"""
        return np.argmax(self.q_table, axis=1)

    def get_q_values(self) -> np.ndarray:
        """Get the Q-table"""
        return self.q_table.copy()


class SARSA:
    """
    SARSA (State-Action-Reward-State-Action) algorithm
    """

    def __init__(self, n_states: int, n_actions: int, learning_rate: float = 0.1,
                 discount_factor: float = 0.9, epsilon: float = 1.0,
                 epsilon_decay: float = 0.995, epsilon_min: float = 0.01):
        self.n_states = n_states
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Initialize Q-table
        self.q_table = np.zeros((n_states, n_actions))

        self.is_fitted = False
        self.training_history = []

    def get_action(self, state: int, training: bool = True) -> int:
        """Get action using epsilon-greedy policy"""
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            return np.argmax(self.q_table[state])

    def update_q_value(self, state: int, action: int, reward: float,
                      next_state: int, next_action: int):
        """Update Q-value using SARSA update rule"""
        # Q(s,a) = Q(s,a) + α[r + γ * Q(s',a') - Q(s,a)]
        current_q = self.q_table[state, action]
        next_q = self.q_table[next_state, next_action]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * next_q - current_q)
        self.q_table[state, action] = new_q

    def decay_epsilon(self):
        """Decay epsilon"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def train(self, env, n_episodes: int = 1000, max_steps_per_episode: int = 100,
              verbose: bool = False) -> List[float]:
        """Train the SARSA agent"""
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            action = self.get_action(state, training=True)
            total_reward = 0
            done = False
            steps = 0

            while not done and steps < max_steps_per_episode:
                next_state, reward, done, info = env.step(action)
                next_action = self.get_action(next_state, training=True)

                self.update_q_value(state, action, reward, next_state, next_action)

                state = next_state
                action = next_action
                total_reward += reward
                steps += 1

            # Decay epsilon
            self.decay_epsilon()

            episode_rewards.append(total_reward)
            self.training_history.append(total_reward)

            if verbose and (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{n_episodes}, "
                      f"Average Reward: {np.mean(episode_rewards[-100:]):.2f}, "
                      f"Epsilon: {self.epsilon:.3f}")

        self.is_fitted = True
        return episode_rewards

    def predict(self, state: int) -> int:
        """Get best action for given state"""
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        return np.argmax(self.q_table[state])


class DeepQLearning:
    """
    Deep Q-Learning using neural network approximation
    """

    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.001,
                 discount_factor: float = 0.99, epsilon: float = 1.0,
                 epsilon_decay: float = 0.995, epsilon_min: float = 0.01,
                 memory_size: int = 2000, batch_size: int = 32):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.memory_size = memory_size
        self.batch_size = batch_size

        # Experience replay memory
        self.memory = deque(maxlen=memory_size)

        # Neural network for Q-value approximation
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()

        self.is_fitted = False
        self.training_history = []

    def _build_model(self):
        """Build neural network model"""
        # Simple neural network implementation
        # In practice, you'd use TensorFlow/Keras or PyTorch
        class SimpleNN:
            def __init__(self, input_size, output_size, learning_rate=0.001):
                self.input_size = input_size
                self.output_size = output_size
                self.learning_rate = learning_rate

                # Initialize weights and biases
                self.W1 = np.random.randn(input_size, 64) * 0.01
                self.b1 = np.zeros((1, 64))
                self.W2 = np.random.randn(64, 32) * 0.01
                self.b2 = np.zeros((1, 32))
                self.W3 = np.random.randn(32, output_size) * 0.01
                self.b3 = np.zeros((1, output_size))

            def forward(self, X):
                # Layer 1
                Z1 = np.dot(X, self.W1) + self.b1
                A1 = np.maximum(0, Z1)  # ReLU

                # Layer 2
                Z2 = np.dot(A1, self.W2) + self.b2
                A2 = np.maximum(0, Z2)  # ReLU

                # Output layer
                Z3 = np.dot(A2, self.W3) + self.b3
                return Z3, A1, A2

            def predict(self, X):
                Z3, _, _ = self.forward(X)
                return Z3

            def train_step(self, X, y):
                # Forward pass
                Z3, A1, A2 = self.forward(X)

                # Compute loss (MSE)
                loss = np.mean((Z3 - y) ** 2)

                # Backward pass (simplified gradient descent)
                dZ3 = 2 * (Z3 - y) / X.shape[0]
                dW3 = np.dot(A2.T, dZ3)
                db3 = np.sum(dZ3, axis=0, keepdims=True)

                dA2 = np.dot(dZ3, self.W3.T)
                dZ2 = dA2 * (A2 > 0)  # ReLU derivative
                dW2 = np.dot(A1.T, dZ2)
                db2 = np.sum(dZ2, axis=0, keepdims=True)

                dA1 = np.dot(dZ2, self.W2.T)
                dZ1 = dA1 * (A1 > 0)  # ReLU derivative
                dW1 = np.dot(X.T, dZ1)
                db1 = np.sum(dZ1, axis=0, keepdims=True)

                # Update weights
                self.W3 -= self.learning_rate * dW3
                self.b3 -= self.learning_rate * db3
                self.W2 -= self.learning_rate * dW2
                self.b2 -= self.learning_rate * db2
                self.W1 -= self.learning_rate * dW1
                self.b1 -= self.learning_rate * db1

                return loss

        return SimpleNN(self.state_size, self.action_size, self.learning_rate)

    def update_target_model(self):
        """Update target model weights"""
        # Copy weights (simplified)
        self.target_model.W1 = self.model.W1.copy()
        self.target_model.b1 = self.model.b1.copy()
        self.target_model.W2 = self.model.W2.copy()
        self.target_model.b2 = self.model.b2.copy()
        self.target_model.W3 = self.model.W3.copy()
        self.target_model.b3 = self.model.b3.copy()

    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory"""
        self.memory.append((state, action, reward, next_state, done))

    def get_action(self, state, training=True):
        """Get action using epsilon-greedy policy"""
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)
        else:
            q_values = self.model.predict(state.reshape(1, -1))
            return np.argmax(q_values[0])

    def replay(self):
        """Train on batch of experiences"""
        if len(self.memory) < self.batch_size:
            return

        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        states = np.array([experience[0] for experience in batch])
        actions = np.array([experience[1] for experience in batch])
        rewards = np.array([experience[2] for experience in batch])
        next_states = np.array([experience[3] for experience in batch])
        dones = np.array([experience[4] for experience in batch])

        # Get current Q values
        current_q = self.model.predict(states)

        # Get target Q values
        target_q = self.target_model.predict(next_states)

        # Update Q values for the batch
        for i in range(self.batch_size):
            if dones[i]:
                current_q[i, actions[i]] = rewards[i]
            else:
                current_q[i, actions[i]] = rewards[i] + self.discount_factor * np.max(target_q[i])

        # Train the model
        loss = self.model.train_step(states, current_q)
        return loss

    def decay_epsilon(self):
        """Decay epsilon"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def train(self, env, n_episodes: int = 1000, max_steps_per_episode: int = 100,
              update_target_freq: int = 10, verbose: bool = False) -> List[float]:
        """Train the Deep Q-Learning agent"""
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            total_reward = 0
            done = False
            steps = 0

            while not done and steps < max_steps_per_episode:
                action = self.get_action(state, training=True)
                next_state, reward, done, info = env.step(action)

                self.remember(state, action, reward, next_state, done)
                loss = self.replay()

                state = next_state
                total_reward += reward
                steps += 1

            # Decay epsilon
            self.decay_epsilon()

            # Update target network
            if episode % update_target_freq == 0:
                self.update_target_model()

            episode_rewards.append(total_reward)
            self.training_history.append(total_reward)

            if verbose and (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{n_episodes}, "
                      f"Average Reward: {np.mean(episode_rewards[-100:]):.2f}, "
                      f"Epsilon: {self.epsilon:.3f}")

        self.is_fitted = True
        return episode_rewards

    def predict(self, state):
        """Get best action for given state"""
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        q_values = self.model.predict(state.reshape(1, -1))
        return np.argmax(q_values[0])


class PolicyGradient:
    """
    Policy Gradient algorithm using REINFORCE
    """

    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.01,
                 discount_factor: float = 0.99):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        # Policy network
        self.policy_network = self._build_policy_network()

        self.is_fitted = False
        self.training_history = []

    def _build_policy_network(self):
        """Build policy network"""
        class PolicyNN:
            def __init__(self, input_size, output_size, learning_rate=0.01):
                self.input_size = input_size
                self.output_size = output_size
                self.learning_rate = learning_rate

                # Initialize weights
                self.W1 = np.random.randn(input_size, 64) * 0.01
                self.b1 = np.zeros((1, 64))
                self.W2 = np.random.randn(64, output_size) * 0.01
                self.b2 = np.zeros((1, output_size))

            def forward(self, X):
                # Layer 1
                Z1 = np.dot(X, self.W1) + self.b1
                A1 = np.maximum(0, Z1)  # ReLU

                # Output layer (softmax)
                Z2 = np.dot(A1, self.W2) + self.b2
                A2 = self._softmax(Z2)
                return A2, A1, Z2

            def _softmax(self, Z):
                exp_Z = np.exp(Z - np.max(Z, axis=1, keepdims=True))
                return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)

            def predict(self, X):
                probs, _, _ = self.forward(X)
                return probs

            def get_action(self, state):
                probs = self.predict(state.reshape(1, -1))[0]
                return np.random.choice(len(probs), p=probs)

            def compute_gradients(self, states, actions, advantages):
                # Forward pass
                probs, A1, Z2 = self.forward(states)

                # One-hot encode actions
                action_onehot = np.zeros_like(probs)
                action_onehot[np.arange(len(actions)), actions] = 1

                # Compute gradients
                dZ2 = (action_onehot - probs) * advantages[:, np.newaxis]
                dW2 = np.dot(A1.T, dZ2)
                db2 = np.sum(dZ2, axis=0, keepdims=True)

                dA1 = np.dot(dZ2, self.W2.T)
                dZ1 = dA1 * (A1 > 0)  # ReLU derivative
                dW1 = np.dot(states.T, dZ1)
                db1 = np.sum(dZ1, axis=0, keepdims=True)

                return dW1, db1, dW2, db2

            def update_weights(self, dW1, db1, dW2, db2):
                self.W1 += self.learning_rate * dW1
                self.b1 += self.learning_rate * db1
                self.W2 += self.learning_rate * dW2
                self.b2 += self.learning_rate * db2

        return PolicyNN(self.state_size, self.action_size, self.learning_rate)

    def get_action(self, state):
        """Get action from policy"""
        return self.policy_network.get_action(state)

    def compute_returns(self, rewards):
        """Compute discounted returns"""
        returns = []
        G = 0
        for reward in reversed(rewards):
            G = reward + self.discount_factor * G
            returns.insert(0, G)
        return np.array(returns)

    def train(self, env, n_episodes: int = 1000, max_steps_per_episode: int = 100,
              verbose: bool = False) -> List[float]:
        """Train the Policy Gradient agent"""
        episode_rewards = []

        for episode in range(n_episodes):
            # Collect trajectory
            states, actions, rewards = [], [], []
            state = env.reset()
            done = False
            steps = 0

            while not done and steps < max_steps_per_episode:
                action = self.get_action(state)
                next_state, reward, done, info = env.step(action)

                states.append(state)
                actions.append(action)
                rewards.append(reward)

                state = next_state
                steps += 1

            # Convert to arrays
            states = np.array(states)
            actions = np.array(actions)
            rewards = np.array(rewards)

            # Compute returns and advantages
            returns = self.compute_returns(rewards)
            advantages = returns - np.mean(returns)  # Baseline subtraction

            # Update policy
            dW1, db1, dW2, db2 = self.policy_network.compute_gradients(states, actions, advantages)
            self.policy_network.update_weights(dW1, db1, dW2, db2)

            total_reward = np.sum(rewards)
            episode_rewards.append(total_reward)
            self.training_history.append(total_reward)

            if verbose and (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{n_episodes}, "
                      f"Average Reward: {np.mean(episode_rewards[-100:]):.2f}")

        self.is_fitted = True
        return episode_rewards

    def predict(self, state):
        """Get best action for given state (greedy)"""
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        probs = self.policy_network.predict(state.reshape(1, -1))[0]
        return np.argmax(probs)


# Environment implementations
class GridWorld:
    """
    Simple Grid World environment for testing RL algorithms
    """

    def __init__(self, size: int = 5):
        self.size = size
        self.n_states = size * size
        self.n_actions = 4  # Up, Down, Left, Right

        # Define rewards
        self.goal_state = (size-1, size-1)
        self.trap_states = [(1, 1), (2, 2)]

        # Reset environment
        self.reset()

    def reset(self):
        """Reset environment to initial state"""
        self.agent_pos = (0, 0)
        self.state = self._pos_to_state(self.agent_pos)
        return self.state

    def _pos_to_state(self, pos):
        """Convert position to state index"""
        return pos[0] * self.size + pos[1]

    def _state_to_pos(self, state):
        """Convert state index to position"""
        return (state // self.size, state % self.size)

    def step(self, action: int):
        """Take action and return next state, reward, done, info"""
        # Action mapping: 0=Up, 1=Down, 2=Left, 3=Right
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = moves[action]

        new_x = max(0, min(self.size - 1, self.agent_pos[0] + dx))
        new_y = max(0, min(self.size - 1, self.agent_pos[1] + dy))

        self.agent_pos = (new_x, new_y)
        self.state = self._pos_to_state(self.agent_pos)

        # Check rewards
        if self.agent_pos == self.goal_state:
            reward = 10
            done = True
        elif self.agent_pos in self.trap_states:
            reward = -10
            done = True
        else:
            reward = -0.1  # Small penalty for each step
            done = False

        return self.state, reward, done, {}

    def render(self):
        """Render the environment"""
        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]
        grid[self.goal_state[0]][self.goal_state[1]] = 'G'
        for trap in self.trap_states:
            grid[trap[0]][trap[1]] = 'T'
        grid[self.agent_pos[0]][self.agent_pos[1]] = 'A'

        for row in grid:
            print(' '.join(row))
        print()


# Utility functions
def plot_training_history(rewards: List[float], title: str = "Training History"):
    """Plot training rewards over episodes"""
    plt.figure(figsize=(10, 6))
    plt.plot(rewards, alpha=0.6)
    plt.plot(pd.Series(rewards).rolling(100).mean(), color='red', linewidth=2)
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title(title)
    plt.legend(['Episode Reward', '100-Episode Moving Average'])
    plt.grid(True)
    plt.show()


def compare_rl_algorithms():
    """Compare different RL algorithms on GridWorld"""
    print("=== Reinforcement Learning Comparison ===")

    # Create environment
    env = GridWorld(size=5)
    n_states = env.n_states
    n_actions = env.n_actions

    algorithms = {
        'Q-Learning': QLearning(n_states, n_actions),
        'SARSA': SARSA(n_states, n_actions)
    }

    results = {}

    for name, algorithm in algorithms.items():
        print(f"\n--- Training {name} ---")
        rewards = algorithm.train(env, n_episodes=500, verbose=True)
        results[name] = rewards

        print(f"Final average reward: {np.mean(rewards[-100:]):.2f}")

    # Plot comparison
    plt.figure(figsize=(12, 8))
    for name, rewards in results.items():
        plt.plot(pd.Series(rewards).rolling(50).mean(), label=name)

    plt.xlabel('Episode')
    plt.ylabel('Average Reward (50-episode window)')
    plt.title('RL Algorithm Comparison on GridWorld')
    plt.legend()
    plt.grid(True)
    plt.show()

    return results


def demonstrate_policy_gradient():
    """Demonstrate Policy Gradient on a simple environment"""
    print("=== Policy Gradient Demonstration ===")

    # Simple environment with continuous states
    class SimpleEnv:
        def __init__(self):
            self.state = 0
            self.n_actions = 2

        def reset(self):
            self.state = np.random.randn()
            return np.array([self.state])

        def step(self, action):
            # Action 0: move left, Action 1: move right
            if action == 0:
                self.state -= 0.1
            else:
                self.state += 0.1

            # Reward is negative distance to target (0)
            reward = -abs(self.state)
            done = abs(self.state) < 0.1
            return np.array([self.state]), reward, done, {}

    env = SimpleEnv()
    agent = PolicyGradient(state_size=1, action_size=2)

    print("Training Policy Gradient agent...")
    rewards = agent.train(env, n_episodes=1000, verbose=True)

    print(f"Final average reward: {np.mean(rewards[-100:]):.2f}")

    # Test the trained agent
    print("\nTesting trained agent:")
    test_rewards = []
    for _ in range(10):
        state = env.reset()
        total_reward = 0
        done = False
        steps = 0
        while not done and steps < 50:
            action = agent.predict(state)
            next_state, reward, done, _ = env.step(action)
            total_reward += reward
            state = next_state
            steps += 1
        test_rewards.append(total_reward)

    print(f"Average test reward: {np.mean(test_rewards):.2f}")


if __name__ == "__main__":
    # Run demonstrations
    compare_rl_algorithms()
    demonstrate_policy_gradient()