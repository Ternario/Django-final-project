import * as urls from "./variables.mjs";

export default class RequestsMethods {
    async getResource(path) {
        const url = `${urls.MAIN_URL}${path}`;
        return await fetch(url)
            .then((response) => {
                if (response.ok) {
                    return response.json();
                }

                return Promise.reject(response);
            })
            .then((response) => response.result)
            .catch((response) => response.status);
    }

    async postResource(path, data) {
        const url = `${urls.MAIN_URL}${path}`;

        const options = {
            method: "POST",
            mode: "cors",
            credentials: "include",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify(data),
        };

        return await fetch(url, options)
            .then((response) => {
                if (response.status === 200) {
                    return response.json();
                }

                return Promise.reject(response);
            })
            .then((response) => response)
            .catch((response) => {
                return response.status;
            });
    }

    async deleteResource(path, data) {
        const url = `${urls.MAIN_URL}${path}`;

        const options = {
            method: "DELETE",
            header: {
                "Content-Type": "application/json; charset=UTF-8",
            },
            body: JSON.stringify(data),
        };

        return await fetch(url, options)
            .then((response) => {
                if (response.ok) {
                    return response.json();
                }

                return Promise.reject(response);
            })
            .then((response) => response.result)
            .catch((response) => response.status);
    }
}
