const express = require("express");
const router = express.Router();
const todoController = require("../controllers/todoController");

router.get("/", todoController.findAll);
router.post("/", todoController.create);
router.get("/:id", todoController.findById);
router.patch("/:id", todoController.markAsDone);
router.delete("/:id", todoController.delete);
router.get("/uuid/:uuid", todoController.findByUUID)
module.exports = router;