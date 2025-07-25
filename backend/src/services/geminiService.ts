import { GoogleGenerativeAI } from "@google/generative-ai";
import dotenv from "dotenv";

dotenv.config();

// Get API key from environment variables
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const MODEL = "gemini-1.5-flash"; // Free tier model

/**
 * Send a message to the Gemini API and get a response
 * @param message - The user's message
 * @returns The AI's response text
 */
export const generateResponse = async (message: string): Promise<string> => {
  try {
    if (!GEMINI_API_KEY) {
      throw new Error("Gemini API key is not configured");
    }

    // Initialize the Google Generative AI client
    const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: MODEL });

    // Generate content using the official SDK
    const result = await model.generateContent(message);
    const response = await result.response;
    const text = response.text();

    if (!text || text.trim() === "") {
      throw new Error("Empty response from Gemini API");
    }

    return text;
  } catch (error) {
    console.error("Gemini API error:", error);

    // Handle specific error cases
    if (error instanceof Error) {
      if (error.message.includes("API key")) {
        throw new Error("Gemini API key is missing or invalid");
      }
      if (error.message.includes("quota")) {
        throw new Error("Gemini API quota exceeded. Please try again later.");
      }
      if (error.message.includes("model")) {
        throw new Error(
          "Gemini model not available. Please check the model name."
        );
      }
    }

    throw new Error(`Failed to generate response: ${(error as Error).message}`);
  }
};
