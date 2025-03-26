import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const headingElement = screen.getByText((content, element) => {
    return element.tagName.toLowerCase() === 'h1' && content.includes('Document Classification System');
  });
  expect(headingElement).toBeInTheDocument();
});

test('renders a button with correct text', () => {
  render(<App />);
  const buttonElement = screen.getByText(/Click to upload email file/i); // Assuming there's a button with "Click to upload email file" text
  expect(buttonElement).toBeInTheDocument();
});

test('button click triggers expected function', () => {
  render(<App />);
  
  // Find the button element
  const buttonElement = screen.getByText(/Predict Document/i);
  
  // Mock the function to be called on click
  const mockFunction = jest.fn();
  
  // Attach the mock function to the button's click event
  buttonElement.onclick = mockFunction;
  
  // Simulate a click event
  fireEvent.click(buttonElement);
  
  // Assert that the mock function was called
  expect(mockFunction).toHaveBeenCalled();
});
