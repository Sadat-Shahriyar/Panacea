import React, { Component } from 'react';
import { Switch, Route, Redirect, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import {
    loginUser,
    loadDocSchedule,
    deleteSchedule,
    loadTimeTable,
    addSchedule,
    getReceptionistAppointments,
    acceptReceptionistAppointment
} from '../Redux/ActionCreator';

import Home from './HomeComponent';
import SignIn from './SignInComponent';
import AppointmentComponent from './Appointment/AppointmentComponent'
import Profile from './ProfileComponent';
import AdminHome from './Admin/Homepage/AdminProfileHomePageComponent';
import PatientHome from './PatientProfileHomePageComponent';
import DoctorHome from './DoctorProfileHomePageComponent';
import Schedule from './Admin/Schedule/ScheduleComponent';
import RegistrationComponent from './Registration/RegistrationComponent'
import ReceptionistHome from './Receptionist/Homepage/ReceptionistHome';
import ReceptionistAppointment from './Receptionist/Appointments/Appointments';

const mapStateToProps = (state) => {
    return {
        User: state.User,
        ScheduleTable: state.ScheduleTable,
        TimeTable: state.TimeTable,
        ReceptionistsAppointments: state.ReceptionistsAppointments
    };
}

const mapDispatchToProps = (dispatch) => {
    return {
        loginUser: (creds) => (dispatch(loginUser(creds))),
        loadDocSchedule: (body) => (dispatch(loadDocSchedule(body))),
        deleteSchedule: (body) => (dispatch(deleteSchedule(body))),
        loadTimeTable: (body) => (dispatch(loadTimeTable(body))),
        addSchedule: (body) => (dispatch(addSchedule(body))),
        getReceptionistAppointments: (body) => (dispatch(getReceptionistAppointments(body))),
        acceptReceptionistAppointment: (body) => (dispatch(acceptReceptionistAppointment(body))),
    };
}

class Main extends Component {
    state = {}
    render() {
        return (
            <React.Fragment>
                <Switch>
                    <Route path='/home'>
                        <Home
                            User={this.props.User}
                        />
                    </Route>
                    <Route path='/sign-in'>
                        <SignIn
                            loginUser={this.props.loginUser}
                            User={this.props.User}
                        />
                    </Route>
                    <Route path='/appointment'>
                        <AppointmentComponent
                            User={this.props.User}
                        />
                    </Route>
                    <Route path='/profile'>
                        <Profile
                            User={this.props.User}
                        />
                    </Route>
                    <Route path="/admin/home">
                        <AdminHome
                            User={this.props.User}
                        />
                    </Route>
                    <Route path="/admin/schedule">
                        <Schedule
                            User={this.props.User}
                            ScheduleTable={this.props.ScheduleTable}
                            TimeTable={this.props.TimeTable}
                            loadDocSchedule={this.props.loadDocSchedule}
                            deleteSchedule={this.props.deleteSchedule}
                            loadTimeTable={this.props.loadTimeTable}
                            addSchedule={this.props.addSchedule}
                        />
                    </Route>
                    <Route path="/doctor/home">
                        <DoctorHome
                            User={this.props.User}
                        />
                    </Route>
                    <Route path="/patient/home">
                        <PatientHome
                            User={this.props.User}
                        />
                    </Route>
                    <Route path="/registration">
                        <RegistrationComponent />
                    </Route>
                    <Route path='/receptionist/home'>
                        <ReceptionistHome
                            User={this.props.User}
                        />
                    </Route>
                    <Route path='/receptionist/appointments'>
                        <ReceptionistAppointment
                            User={this.props.User}
                            ReceptionistsAppointments={this.props.ReceptionistsAppointments}
                            getReceptionistAppointments={this.props.getReceptionistAppointments}
                            acceptReceptionistAppointment={this.props.acceptReceptionistAppointment}
                        />
                    </Route>
                    <Redirect to="/home" />
                </Switch>
            </React.Fragment>
        );
    }
}

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Main));