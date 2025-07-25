import mongoose, { Schema, Document } from 'mongoose';

// Define the Message interface
export interface IMessage extends Document {
  chatId: string;
  user: string;
  bot: string;
  timestamp: Date;
}

// Create the Message schema
const MessageSchema: Schema = new Schema({
  chatId: {
    type: String,
    required: true,
    index: true
  },
  user: {
    type: String,
    required: true
  },
  bot: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// Export the Message model
export default mongoose.model<IMessage>('Message', MessageSchema);