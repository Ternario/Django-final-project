import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

import AuthorizationService from "../../../services/authorizationService.mjs";

export default function Registration() {
    const signUpRequest = new AuthorizationService();

    const navigate = useNavigate();

    const defaultFormList = {
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        confirm_password: "",
    };

    const [formList, setFormList] = useState(defaultFormList);

    const registration = async (e) => {
        e.preventDefault();

        await signUpRequest.signUp(formList).then((response) => {
            switch (response) {
                case 400:
                    console.log("error");
                    break;
                default:
                    navigate("/signIn");
                    break;
            }
        });
    };

    return (
        <div className="home">
            <Form onSubmit={(e) => registration(e)}>
                <Form.Group className="mb-3" controlId="signUpFirstName">
                    <Form.Label>First Name</Form.Label>
                    <Form.Control
                        type="text"
                        placeholder="Enter your first name"
                        value={formList.first_name}
                        onChange={(e) =>
                            setFormList((prevState) => ({
                                ...prevState,
                                first_name: e.target.value,
                            }))
                        }
                    />
                    {/* <Form.Text className="text-muted">We'll never share your email with anyone else.</Form.Text> */}
                </Form.Group>
                <Form.Group className="mb-3" controlId="signUpLastName">
                    <Form.Label>Last Name</Form.Label>
                    <Form.Control
                        type="text"
                        placeholder="Enter your last name"
                        value={formList.last_name}
                        onChange={(e) =>
                            setFormList((prevState) => ({
                                ...prevState,
                                last_name: e.target.value,
                            }))
                        }
                    />
                    {/* <Form.Text className="text-muted">We'll never share your email with anyone else.</Form.Text> */}
                </Form.Group>
                <Form.Group className="mb-3" controlId="siugnUpEmail">
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

                <Form.Group className="mb-3" controlId="signUpPassword">
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
                <Form.Group className="mb-3" controlId="signUpConfirmPassword">
                    <Form.Label>Confirm Password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder=" Confirm password"
                        value={formList.confirm_password}
                        onChange={(e) =>
                            setFormList((prevState) => ({
                                ...prevState,
                                confirm_password: e.target.value,
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
