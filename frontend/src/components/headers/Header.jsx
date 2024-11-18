import { NavLink } from "react-router-dom";

import styles from "./Header.module.css";
import DropdownMenu from "./dropdown/DropdownMenu";

export default function Header({ isAuthenticated, userData, toggleUserData }) {
    return (
        <div className={styles.Header}>
            <div className={styles.HeaderMenu}>
                <div className={styles.HeaderMenuRight}>
                    <NavLink to="/" className={styles.HomeLink}>
                        <h1 className={styles.HomeTitle}>Django-booking</h1>
                    </NavLink>
                </div>
                <div className={styles.HeaderMenuLeft}>
                    {isAuthenticated ? (
                        <div className={styles.Authenticated}>
                            <div className="notification">{/* icon */}</div>
                            <DropdownMenu userData={userData} toggleUserData={toggleUserData} />
                        </div>
                    ) : (
                        <div className={styles.Everywan}>
                            <NavLink to="/signIn" className={styles.Sign}>
                                Sign In
                            </NavLink>
                            <NavLink to="/signUp" className={styles.Sign}>
                                Sign Up
                            </NavLink>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
