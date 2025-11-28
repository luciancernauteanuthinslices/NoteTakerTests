export default {
    account:{
        login: '/users/login',
        logout: '/users/logout',
        profile: '/users/profile',
        patchProfile: '/users/profile',
    },
    notes:{
        getNotes: '/notes',
        postNote: '/notes',
        deleteNote: `/notes/`,  //use in tests with noteId -> /notes/{id}
        updateNote: `/notes/`, //use in tests with noteId -> /notes/{id}
    }
}