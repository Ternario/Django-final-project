import { useState } from "react";
import { NavLink } from "react-router-dom";

import styles from "./DropdownMenu.module.css";

import AuthorizationService from "../../../services/authorizationService.mjs";

export default function DropdownMenu({ userData, toggleUserData }) {
    const logout = new AuthorizationService();

    const [isOpen, setIsOpen] = useState(false);
    return (
        <>
            <div className={styles.DropdownMenu}>
                <button onClick={() => setIsOpen(!isOpen)}>{`${userData.first_name} ${userData.last_name}`}</button>
                {isOpen && (
                    <ul className={styles.Menu}>
                        <li className={styles.MenuItem}>
                            <NavLink to="/profile" className={styles.MenuLink}>
                                Profile
                            </NavLink>
                        </li>
                        <li className={styles.MenuItem}>
                            <NavLink to="/reservation" className={styles.MenuLink}>
                                Reservation
                            </NavLink>
                        </li>
                        <li className={styles.MenuItem}>
                            <NavLink to="/ads" className={styles.MenuLink}>
                                Your ads
                            </NavLink>
                        </li>
                        <li className={styles.MenuItem}>
                            <button
                                className={styles.MenuButton}
                                onClick={() => {
                                    logout.logOut();
                                    // toggleUserData();
                                }}
                            >
                                Logeout
                            </button>
                        </li>
                    </ul>
                )}
            </div>
        </>
    );
}
