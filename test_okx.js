const axios = require('axios');
const crypto = require('crypto');

// Load from .env
require('dotenv').config();

const OKX_API_KEY = process.env.OKX_API_KEY;
const OKX_SECRET_KEY = process.env.OKX_SECRET_KEY;
const OKX_PASSPHRASE = process.env.OKX_PASSPHRASE;
const OKX_BASE_URL = process.env.OKX_BASE_URL || 'https://www.okx.com';

function getHeaders(method, path, body = '') {
  const timestamp = new Date().toISOString();
  const message = timestamp + method.toUpperCase() + path + body;
  const signature = crypto.createHmac('sha256', OKX_SECRET_KEY).update(message).digest('base64');
  
  return {
    'OK-ACCESS-KEY': OKX_API_KEY,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': OKX_PASSPHRASE,
    'Content-Type': 'application/json'
  };
}

async function testConnection() {
  try {
    console.log('Testing OKX API connection...\n');
    const path = '/api/v5/account/account-position-risk';
    const headers = getHeaders('GET', path + '?instType=SWAP');
    
    const response = await axios.get(OKX_BASE_URL + path + '?instType=SWAP', { headers });
    console.log('✅ OKX API connection successful!');
    console.log('Status:', response.status);
    console.log('Account data:', JSON.stringify(response.data, null, 2));
  } catch (error) {
    console.log('❌ API Error:', error.response?.status, error.response?.statusText);
    console.log('Error details:', error.response?.data || error.message);
  }
}

testConnection();
