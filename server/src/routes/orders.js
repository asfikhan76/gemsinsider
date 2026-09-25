import express from 'express'
import Order from '../models/Order.js'
import authMiddleware from '../middleware/auth.js'

const router = express.Router()

// Get all orders (admin only)
router.get('/', authMiddleware, async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Admin access required' })
    }
    const orders = await Order.find().sort({ createdAt: -1 })
    res.json(orders.map(order => ({ id: order._id, ...order.toObject() })))
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch orders' })
  }
})

// Update order status
router.put('/:id', authMiddleware, async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Admin access required' })
    }
    const order = await Order.findByIdAndUpdate(req.params.id, { status: req.body.status }, { new: true })
    if (!order) return res.status(404).json({ message: 'Order not found' })
    res.json(order)
  } catch (error) {
    res.status(500).json({ message: 'Failed to update order' })
  }
})

// Delete order
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Admin access required' })
    }
    await Order.findByIdAndDelete(req.params.id)
    res.json({ message: 'Order deleted' })
  } catch (error) {
    res.status(500).json({ message: 'Failed to delete order' })
  }
})

// Create order
router.post('/', authMiddleware, async (req, res) => {
  try {
    const { items } = req.body
    const order = new Order({
      userId: req.user.uid,
      userEmail: req.user.email,
      items
    })
    await order.save()
    res.status(201).json(order)
  } catch (error) {
    res.status(500).json({ message: 'Failed to create order' })
  }
})

export default router
