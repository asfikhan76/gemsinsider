import express from 'express'
import Contact from '../models/Contact.js'

const router = express.Router()

router.post('/', async (req, res) => {
  try {
    const { name, email, subject, message } = req.body
    const contact = new Contact({ name, email, subject, message })
    await contact.save()
    res.status(201).json({ message: 'Message sent successfully' })
  } catch (error) {
    console.error('Contact error:', error)
    res.status(500).json({ message: 'Failed to send message. Please try again.' })
  }
})

export default router
