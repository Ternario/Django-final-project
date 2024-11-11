import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import AuthorizationService from "../../../services/authorizationService.mjs";

export default function SignIn({ toggleUserData }) {
    const signInRequest = new AuthorizationService();
    const navigate = useNavigate();

    const [formList, setFormList] = useState({ email: "", password: "" });

    const signIn = async (e) => {
        e.preventDefault();

        await signInRequest.signIn(formList).then((response) => {
            switch (response) {
                case 400:
                    console.log(400);
                    break;

                default:
                    toggleUserData(response);
                    // navigate("/search");
                    break;
            }
        });
    };

    return (
        <div className="home">
            <Form onSubmit={(e) => signIn(e)}>
                <Form.Group className="mb-3" controlId="signInEmail">
                    <Form.Label>Email address</Form.Label>
                    <Form.Control
                        type="email"
                        placeholder="Enter email"
                        value={formList.email}
                        onChange={(e) =>
                            setFormList((prevState) => ({
                                ...prevState,
                                email: e.target.value,
                            }))
                        }
                    />
                    {/* <Form.Text className="text-muted">We'll never share your email with anyone else.</Form.Text> */}
                </Form.Group>

                <Form.Group className="mb-3" controlId="signInPassword">
                    <Form.Label>Password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder="Password"
                        value={formList.password}
                        onChange={(e) =>
                            setFormList((prevState) => ({
                                ...prevState,
                                password: e.target.value,
                            }))
                        }
                    />
                </Form.Group>
                {/* <Form.Group className="mb-3" controlId="formBasicCheckbox">
                    <Form.Check type="checkbox" label="Check me out" />
                </Form.Group> */}
                <Button variant="primary" type="submit">
                    Submit
                </Button>
            </Form>
        </div>
    );
}
