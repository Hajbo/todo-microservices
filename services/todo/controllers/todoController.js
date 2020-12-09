const TodoItem = require("../models/todoItemModel");


exports.create = (req, res) => {
  if (!req.body.uuid || !req.body.task) {
    return res.status(400).send({
      message: "Required field can not be empty, got:  " + req.body.uuid + "   ---  " + req.body.task ,
    });
  }
  const todoItem = new TodoItem({
    uuid: req.body.uuid,
    task: req.body.task
  });
  todoItem
    .save()
    .then((data) => {
      res.send(data);
    })
    .catch((err) => {
      res.status(500).send({
        message: err.message || "Some error occurred while creating the User.",
      });
    });
};


exports.delete = (req, res) => {
    TodoItem.findByIdAndRemove(req.params.id)
      .then((todo) => {
        if (!todo) {
          return res.status(404).send({
            message: "Todo not found ",
          });
        }
        res.send({ message: "Todo deleted successfully!" });
      })
      .catch((err) => {
        return res.status(500).send({
          message: "Could not delete todo ",
        });
      });
  };


  exports.findById = (req, res) => {
    TodoItem.findById(req.params.id)
      .then((todo) => {
        if (!todo) {
          return res.status(404).send({
            message: "Todo not found with id " + req.params.id,
          });
        }
        return res.status(200).send(todo);
      })
      .catch((err) => {
        return res.status(500).send({
          message: "Error retrieving todo with id " + req.params.id,
        });
      });
  };


exports.findByUUID = (req, res) => {
    TodoItem.find({"uuid": req.params.uuid})
      .then((todo) => {
        if (!todo) {
          return res.status(404).send({
            message: "Todo not found with uuid " + req.params.uuid,
          });
        }
        res.status(200).send(todo);
        console.log(todo);
      })
      .catch((err) => {
        return res.status(500).send({
          message: "Error retrieving todo with uuid " + req.params.uuid,
        });
      });
  };



exports.markAsDone = (req, res) => {
    TodoItem.findByIdAndUpdate(req.params.id, {isDone: true}, { new: true })
      .then((todo) => {
        if (!todo) {
          return res.status(404).send({
            message: "no Todo found",
          });
        }
        res.status(200).send(todo);
      })
      .catch((err) => {
        return res.status(404).send({
          message: "error while updating the post",
        });
      });
  };


exports.findAll = (req, res) => {
  TodoItem.find()
    .sort({ uuid: -1 })
    .then((todos) => {
    res.status(200).send(todos);
    })
    .catch((err) => {
    res.status(500).send({
        message: err.message || "Error Occured",
    });
    });
};