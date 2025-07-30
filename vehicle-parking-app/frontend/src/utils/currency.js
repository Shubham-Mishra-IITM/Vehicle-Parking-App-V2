// Currency formatting utilities for Indian Rupees
/**
 * Format amount in INR with currency symbol
 * @param {number} amount - Amount in INR
 * @returns {string} Formatted INR amount
 */
export const formatINR = (amount) => {
  // Handle null, undefined, or empty values
  if (amount === null || amount === undefined || amount === '') return '₹0.00'
  
  // Convert to number if it's a string
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount
  
  // Check if conversion resulted in a valid number
  if (isNaN(numAmount)) return '₹0.00'
  
  return `₹${numAmount.toFixed(2)}`
}
