import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: 'YOUR_OPENAI_API_KEY_HERE',
  dangerouslyAllowBrowser: true
});

export const createChatCompletion = async (messages: { role: 'user', content: string, name: string }[]) => {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are Maya, a friendly and helpful AI assistant for the MayaCode User Dashboard. Your goal is to assist users with understanding their dashboard, profile information, suggested actions, and documents. Be concise and helpful. If a user asks for something you cannot do (e.g., perform actions on their behalf directly through this chat, or provide real-time external data beyond your training), politely inform them of your capabilities. You can provide information based on the user's profile and the general functionality of the dashboard but you do not have direct access to their live data unless it is explicitly provided in the prompt during this conversation.",
          name: "system"
        },
        ...messages
      ],
      temperature: 0.7,
      stream: true
    });

    return response;
  } catch (error) {
    console.error('Error in OpenAI chat completion:', error);
    throw error;
  }
}; 