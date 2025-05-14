import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Container,
  IconButton,
  Card,
  CardContent,
} from '@mui/material';
import { Send as SendIcon, Image as ImageIcon } from '@mui/icons-material';
import axios from 'axios';
import { Message, Product } from '../types';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() && !selectedImage) return;

    const userMessage: Message = {
      type: 'text',
      content: input,
      sender: 'user',
    };

    if (selectedImage) {
      userMessage.imageUrl = URL.createObjectURL(selectedImage);
    }

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setSelectedImage(null);

    try {
      let requestData: any = {};
      
      if (selectedImage) {
        // Convert image to base64
        const reader = new FileReader();
        reader.readAsDataURL(selectedImage);
        await new Promise((resolve) => {
          reader.onload = () => {
            const base64String = reader.result as string;
            // Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
            requestData.raw_image = base64String.split(',')[1];
            resolve(null);
          };
        });
      }
      
      if (input.trim()) {
        requestData.message = input;
      }
      
      if (sessionId) {
        requestData.session_id = sessionId;
      }

      const response = await axios.post('http://localhost:8000/chat', requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      setSessionId(response.data.session_id);

      try {
        // First try to parse the response as JSON
        const parsedResponse = JSON.parse(response.data.response);
        
        // Check if it's already in our message format
        if (parsedResponse.type === 'json' && parsedResponse.content) {
          // The content is already a parsed object, no need to parse again
          const assistantMessage: Message = {
            type: 'json',
            content: typeof parsedResponse.content === 'string' 
              ? parsedResponse.content 
              : JSON.stringify(parsedResponse.content),
            sender: 'assistant',
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }
        // Check if it's a product object
        else if (parsedResponse.name && parsedResponse.description && parsedResponse.brand && 
                parsedResponse.category && parsedResponse.price !== undefined) {
          // It's a product object, create a message with type 'json'
          const assistantMessage: Message = {
            type: 'json',
            content: JSON.stringify(parsedResponse),
            sender: 'assistant',
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }
        // Check if it's a text message with type and content
        else if (parsedResponse.type === 'text' && parsedResponse.content) {
          // It's a text message, use the content directly
          const assistantMessage: Message = {
            type: 'text',
            content: parsedResponse.content,
            sender: 'assistant',
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }
        else {
          // It's not in any known format, treat as text
          const assistantMessage: Message = {
            type: 'text',
            content: response.data.response,
            sender: 'assistant',
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }
      } catch {
        // If parsing fails, treat as text
        const assistantMessage: Message = {
          type: 'text',
          content: response.data.response,
          sender: 'assistant',
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
      }
      
      const errorMessage: Message = {
        type: 'text',
        content: `Error: ${error.response?.data?.detail || 'Unknown error occurred'}`,
        sender: 'assistant',
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const renderMessage = (message: Message) => {
    const isUser = message.sender === 'user';
    const backgroundColor = isUser ? '#e3f2fd' : '#f5f5f5';

    if (message.type === 'json') {
      try {
        // Parse the content if it's a string, otherwise use it directly
        const product: Product = typeof message.content === 'string' 
          ? JSON.parse(message.content)
          : message.content;

        return (
          <Box
            sx={{
              display: 'flex',
              justifyContent: isUser ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Card sx={{ maxWidth: 345, backgroundColor }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {product.name}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {product.brand}
                </Typography>
                <Typography variant="body2" paragraph>
                  {product.description}
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                  Category: {product.category}
                </Typography>
                <Typography variant="h6" color="primary" gutterBottom>
                  ${product.price.toLocaleString()}
                </Typography>
                {product.image_encoded && (
                  <Box sx={{ mt: 2 }}>
                    <img
                      src={`data:image/jpeg;base64,${product.image_encoded}`}
                      alt={product.name}
                      style={{
                        width: '100%',
                        height: 'auto',
                        maxHeight: '200px',
                        objectFit: 'contain',
                        borderRadius: '4px',
                      }}
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>
        );
      } catch (error) {
        console.error('Error parsing product JSON:', error);
        return (
          <Box
            sx={{
              display: 'flex',
              justifyContent: isUser ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                backgroundColor,
                maxWidth: '70%',
                borderRadius: 2,
              }}
            >
              <Typography color="error">Error displaying product information</Typography>
            </Paper>
          </Box>
        );
      }
    }

    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Paper
          elevation={1}
          sx={{
            p: 2,
            backgroundColor,
            maxWidth: '70%',
            borderRadius: 2,
          }}
        >
          {message.imageUrl && (
            <Box sx={{ mb: 1 }}>
              <img
                src={message.imageUrl}
                alt="Uploaded"
                style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '4px' }}
              />
            </Box>
          )}
          <Typography>{message.content}</Typography>
        </Paper>
      </Box>
    );
  };

  return (
    <Container maxWidth="md" sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" sx={{ my: 2, textAlign: 'center' }}>
        Shopping Assistant
      </Typography>
      
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          mb: 2,
          p: 2,
          backgroundColor: '#fff',
          borderRadius: 2,
          boxShadow: 1,
        }}
      >
        {messages.map((message, index) => (
          <Box key={index}>{renderMessage(message)}</Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <input
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          id="image-upload"
          onChange={handleImageUpload}
        />
        <label htmlFor="image-upload">
          <IconButton component="span" color="primary">
            <ImageIcon />
          </IconButton>
        </label>
        {selectedImage && (
          <Typography variant="body2" sx={{ alignSelf: 'center' }}>
            {selectedImage.name}
          </Typography>
        )}
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <Button
          variant="contained"
          color="primary"
          endIcon={<SendIcon />}
          onClick={handleSend}
        >
          Send
        </Button>
      </Box>
    </Container>
  );
};

export default Chat; 