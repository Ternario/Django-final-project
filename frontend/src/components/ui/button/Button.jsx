import styles from "./Button.module.css";

function Button(props) {
    const { children } = props;
    return (
        <button {...props} className={styles.button}>
            {children}
        </button>
    );
}

export default Button;
