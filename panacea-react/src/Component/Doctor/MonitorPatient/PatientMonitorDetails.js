import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
import {
    withStyles, AppBar, Drawer, Toolbar, List, Divider, CssBaseline, Typography,
    Card, Container, Grid, Box, Link, ListItem, Button, lighten
} from '@material-ui/core';
import { mainListItems, secondaryListItems } from '../Homepage/listItems';
import CopyRight from '../../Copyright';
import { baseUrl } from '../../../Redux/ActionCreator';
import PatientMonitorTable from './PatientMonitorTable';
import BloodPressureGraph from './BloodPressureGraph';
import HeartBeatGraph from './HeartRateGraph';
import OxygenLevelBreathingRateGraph from './OxygenBreathingGraph';

const drawerWidth = 240;

const styles = (theme) => ({
    root: {
        display: 'flex',
        '& > *': {
            borderBottom: 'unset',
        },
    },
    appBar: {
        zIndex: theme.zIndex.drawer + 1,
    },
    drawer: {
        width: drawerWidth,
        flexShrink: 0,
    },
    drawerPaper: {
        width: drawerWidth,
    },
    drawerContainer: {
        overflow: 'auto',
    },
    content: {
        flexGrow: 1,
        padding: theme.spacing(3),
    },
    paper: {
        padding: theme.spacing(2),
        display: 'flex',
        overflow: 'auto',
        flexDirection: 'column',
    },
    fixedHeight: {
        height: 240,
    },
    highlightImportant: {
        color: theme.palette.secondary.main,
        backgroundColor: lighten(theme.palette.secondary.light, 0.85),
    },
    highlightUnread: {
        color: theme.palette.text.primary,
        backgroundColor: theme.palette.action.hover,
    }

});

class PatientMonitorDetail extends Component {
    timeOutId;
    constructor(props) {
        super(props);

        this.state = {
            monitor_data: null,
            patientInfo: null
        }

        this.handleLogout = this.handleLogout.bind(this);
        this.renderPage = this.renderPage.bind(this);
        this.fetchData = this.fetchData.bind(this);
        this.refreshMonitorData = this.refreshMonitorData.bind(this);
    }


    fetchData(body) {
        fetch(baseUrl + 'checkup/doctor/get-patient-monitor-data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        })
            .then((response) => {
                console.log(response);
                if (response.ok) {
                    return response;
                }
                else {
                    let err = new Error('Error ' + response.status + ': ' + response.statusText);
                    err.response = response;
                    throw err;
                }
            })
            .then((response) => response.json())
            .then((response) => {
                if (response.success) {
                    this.setState({ monitor_data: response.monitor_data, patientInfo: response.patient_info })
                    this.timeOutId = setTimeout(this.refreshMonitorData.bind(this), 3000);
                }
                else {
                    let err = new Error(response.errorMessage);
                    err.response = response;
                    throw err;
                }
            })
            .catch((err) => {
                alert(err.message)
            });
    }

    refreshMonitorData() {
        let creds = JSON.parse(this.props.User.creds);
        let body = { 'userID': creds.userId, 'token': this.props.User.token, 'patient_id': this.props.patient_id }
        this.fetchData(body);
    }
    componentDidMount() {
        let creds = JSON.parse(this.props.User.creds);
        let body = { 'userID': creds.userId, 'token': this.props.User.token, 'patient_id': this.props.patient_id }
        this.fetchData(body);
    }

    componentWillUnmount() {
        clearTimeout(this.timeOutId);
    }

    handleLogout() {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('creds');
        sessionStorage.removeItem('userData');
        sessionStorage.removeItem('userCategory');
    }

    renderPage() {

        const { classes } = this.props;

        if (this.props.User.isAuthenticated && this.props.User.category === 'doctor') {
            let userData = JSON.parse(this.props.User.userData);
            return (
                <div className={classes.root}>
                    <CssBaseline />
                    <AppBar position="fixed" className={classes.appBar}>
                        <Toolbar>
                            <Typography variant="h6" noWrap>
                                Doctor
                            </Typography>
                            <Link color='inherit' href='http://localhost:3000/home' onClick={() => { this.handleLogout() }} style={{ marginLeft: 'auto' }}>
                                Logout
                            </Link>
                        </Toolbar>
                    </AppBar>
                    <Drawer
                        className={classes.drawer}
                        variant="permanent"
                        classes={{
                            paper: classes.drawerPaper,
                        }}
                    >
                        <Toolbar />
                        <div className={classes.drawerContainer}>
                            <List>{mainListItems}</List>
                            <Divider />
                            <List>{secondaryListItems}</List>
                        </div>
                    </Drawer>


                    <main className={classes.content}>
                        <Toolbar />
                        <div />
                        <Container maxWidth="lg" >
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    {this.state.patientInfo === null ? null :
                                        <Card style={{ padding: 10 }}>
                                            <Typography variant='h6'>Patient name: {this.state.patientInfo.patient_name}</Typography>
                                            <Typography variant='body1'>Admission date: {this.state.patientInfo.admission_date}</Typography>
                                        </Card>
                                    }
                                </Grid>
                                <Grid item xs={12}>
                                    <BloodPressureGraph
                                        monitor_data={this.state.monitor_data}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <HeartBeatGraph
                                        monitor_data={this.state.monitor_data}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <OxygenLevelBreathingRateGraph
                                        monitor_data={this.state.monitor_data}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    {this.state.monitor_data === null ? null :
                                        <PatientMonitorTable
                                            monitor_data={this.state.monitor_data}
                                        />
                                    }

                                </Grid>
                            </Grid>
                            <Box pt={4}>
                                {CopyRight}
                            </Box>
                        </Container>
                    </main>
                </div>
            );
        }
        else {
            return (<Redirect to='/sign-in' />);
        }
    }

    render() {
        const page = this.renderPage();
        return (
            <React.Fragment>
                {page}
            </React.Fragment>
        );
    }
}

export default withStyles(styles)(PatientMonitorDetail);