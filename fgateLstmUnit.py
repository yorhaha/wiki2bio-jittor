import jittor as jt
import numpy as np

class fgateLstmUnit(jt.Module):
    def __init__(self, hidden_size, input_size, field_size):
        self.hidden_size = hidden_size
        self.input_size = input_size
        self.field_size = field_size

        self.linear = jt.nn.Linear(self.input_size+self.hidden_size, 4*self.hidden_size)
        self.linear1 = jt.nn.Linear(self.field_size, 2*self.hidden_size)
        self.params = {'linear': self.linear, 'linear1': self.linear1}

    def execute(self, x, fd, s, finished = None):
        h_prev, c_prev = s  # batch * hidden_size

        x = jt.contrib.concat([x, h_prev], 1)
        # fd = tf.concat([fd, h_prev], 1)
        i, j, f, o = jt.chunk(self.linear(x), 4, 1)
        r, d = jt.chunk(self.linear1(fd), 2, 1)
        # Final Memory cell
        c = jt.sigmoid(f+1.0) * c_prev + jt.sigmoid(i) * jt.tanh(j) + jt.sigmoid(r) * jt.tanh(d)  # batch * hidden_size
        h = jt.sigmoid(o) * jt.tanh(c)

        out, state = h, (h, c)
        if finished is not None:
            finished = finished.unsqueeze(1)
            inds = jt.where(finished)[0]
            out[inds] = 0
            state[0][inds] = h_prev[inds]
            state[1][inds] = c_prev[inds]
            # out = jt.array(np.where(finished, np.zeros_like(h), np.array(h)))
            # state = (jt.array(np.where(finished, h_prev, h)), jt.array(np.where(finished, c_prev, c)))

        return out, state
    
    def save(self, path):
        jt.save(self.params, path)
    
    def load(self, path):
        params = jt.load(path)
        for param in params:
            self.params[param].load_state_dict(params[param].state_dict())
