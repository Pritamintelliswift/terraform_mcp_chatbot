import express, { Request, Response } from 'express';
import Message from '../models/message';
import { generateResponse } from '../services/geminiService';

const router = express.Router();

// Validate request body
const validateChatRequest = (req: Request, res: Response, next: Function) => {
  const { message, chatId } = req.body;
  
  if (!message || typeof message !== 'string' || message.trim() === '') {
    return res.status(400).json({ error: 'Message is required and must be a non-empty string' });
  }
  
  if (!chatId || typeof chatId !== 'string') {
    return res.status(400).json({ error: 'Chat ID is required and must be a string' });
  }
  
  next();
};

// POST /api/chat - Send a message to the chatbot
router.post('/', validateChatRequest, async (req: Request, res: Response) => {
  try {
    const { message, chatId } = req.body;
    
    // Generate response using Gemini API
    const botReply = await generateResponse(message);
    
    // Save the conversation to MongoDB
    const newMessage = new Message({
      chatId,
      user: message,
      bot: botReply
    });
    
    await newMessage.save();
    
    // Return the response
    res.status(200).json({
      reply: botReply,
      chatId
    });
  } catch (error) {
    console.error('Chat API error:', error);
    
    // Handle specific error cases
    if ((error as Error).message.includes('API key')) {
      return res.status(500).json({ 
        error: 'Configuration error', 
        message: 'API key is missing or invalid' 
      });
    }
    
    res.status(500).json({ 
      error: 'Failed to process message',
      message: process.env.NODE_ENV === 'production' 
        ? 'An error occurred while processing your message' 
        : (error as Error).message
    });
  }
});

// GET /api/chat/history/:chatId - Get conversation history for a specific chat
router.get('/history/:chatId', async (req: Request, res: Response) => {
  try {
    const { chatId } = req.params;
    const history = await Message.find({ chatId }).sort({ timestamp: 1 });
    res.status(200).json(history);
  } catch (error) {
    console.error('History API error:', error);
    res.status(500).json({ error: 'Failed to retrieve chat history' });
  }
});

// GET /api/chat/sessions - Get all chat sessions
router.get('/sessions', async (req: Request, res: Response) => {
  try {
    const sessions = await Message.aggregate([
      {
        $group: {
          _id: '$chatId',
          title: { $first: '$user' },
          lastMessage: { $last: '$bot' },
          timestamp: { $last: '$timestamp' },
          messageCount: { $sum: 1 }
        }
      },
      {
        $sort: { timestamp: -1 }
      },
      {
        $limit: 50
      },
      {
        $project: {
          id: '$_id',
          title: { $substr: ['$title', 0, 50] },
          preview: { $substr: ['$lastMessage', 0, 100] },
          timestamp: 1,
          messageCount: 1,
          _id: 0
        }
      }
    ]);
    
    res.status(200).json(sessions);
  } catch (error) {
    console.error('Sessions API error:', error);
    res.status(500).json({ error: 'Failed to retrieve chat sessions' });
  }
});

// DELETE /api/chat/session/:chatId - Delete a chat session
router.delete('/session/:chatId', async (req: Request, res: Response) => {
  try {
    const { chatId } = req.params;
    await Message.deleteMany({ chatId });
    res.status(200).json({ message: 'Chat session deleted successfully' });
  } catch (error) {
    console.error('Delete session API error:', error);
    res.status(500).json({ error: 'Failed to delete chat session' });
  }
});

export default router;