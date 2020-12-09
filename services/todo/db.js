const mongoose = require('mongoose');

var connectWithRetry = function() {
    return mongoose.connect('mongodb://mongo:27017/todo', function(err) {
        if (err) {
            console.error('Failed to connect to mongo on startup - retrying in 1 sec', err);
            setTimeout(connectWithRetry, 1000);
        }
    });
};
connectWithRetry();

module.exports = mongoose;