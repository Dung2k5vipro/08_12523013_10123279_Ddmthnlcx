const mongoose = require('mongoose');

const config = require('./env');

async function connectDatabase() {
  try {
    await mongoose.connect(config.MONGODB_URI);
    console.log('Kết nối MongoDB thành công');
  } catch (error) {
    console.error(`Kết nối MongoDB thất bại: ${error.message}`);
    throw error;
  }
}

async function disconnectDatabase() {
  if (mongoose.connection.readyState !== 0) {
    await mongoose.disconnect();
    console.log('Đã đóng kết nối MongoDB');
  }
}

module.exports = { connectDatabase, disconnectDatabase };