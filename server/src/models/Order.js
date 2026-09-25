import mongoose from 'mongoose'

const orderSchema = new mongoose.Schema({
  userId: { type: String, required: true },
  userEmail: { type: String, required: true },
  items: [{
    id: String,
    name: String,
    category: String,
    price: String
  }],
  status: { type: String, enum: ['New', 'Confirmed', 'Shipped', 'Completed', 'Cancelled'], default: 'New' },
  createdAt: { type: Date, default: Date.now }
})

export default mongoose.model('Order', orderSchema)
