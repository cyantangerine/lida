import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: localStorage.getItem('access_token') || '',
    userInfo: JSON.parse(localStorage.getItem('user_info') || '{}'),
    currentChat: null,
    chats: []
  },
  getters: {
    isLoggedIn: state => !!state.token,
    currentUser: state => state.userInfo
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('access_token', token)
    },
    SET_USER_INFO(state, userInfo) {
      state.userInfo = userInfo
      localStorage.setItem('user_info', JSON.stringify(userInfo))
    },
    SET_CURRENT_CHAT(state, chat) {
      state.currentChat = chat
    },
    SET_CHATS(state, chats) {
      state.chats = chats
    },
    LOGOUT(state) {
      state.token = ''
      state.userInfo = {}
      state.currentChat = null
      state.chats = []
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
    }
  },
  actions: {
    login({ commit }, { username, password }) {
      return new Promise((resolve, reject) => {
        // 这里调用 API
        commit('SET_TOKEN', 'mock_token')
        resolve()
      })
    },
    logout({ commit }) {
      commit('LOGOUT')
    }
  },
  modules: {}
})
