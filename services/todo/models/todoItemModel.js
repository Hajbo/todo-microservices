const mongoose = require("../db");

const schema = new mongoose.Schema(
  {
    task: {
      desc: "The user's email address.",
      trim: true,
      type: String,
      required: true,
    },
    uuid: {
      desc: "unique user uuid across the microservices",
      trim: true,
      type: String,
      required: true,
      index: true,
    },
    isDone: {
      desc: "task is done",
      type: Boolean,
      default: false,
      required: true,
    },
  },
  {
    strict: true,
    versionKey: false,
    timestamps: { createdAt: "createdAt", updatedAt: "updatedAt" },
  }
);

module.exports = mongoose.model("TodoItem", schema);