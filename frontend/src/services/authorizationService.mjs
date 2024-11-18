import RequestsMethods from "./methods.mjs";

export default class AuthorizationService extends RequestsMethods {
    async signUp(data) {
        const url = "registration/";

        return await super.postResource(url, data);
    }

    async signIn(data) {
        const url = "login/";

        return await super.postResource(url, data);
    }

    async logOut(data) {
        const url = "logout/";

        return await super.postResource(url, data);
    }

    async deleteUser(data) {
        const url = "authorization/delete";

        return await super.deleteResource(url, data);
    }
}
